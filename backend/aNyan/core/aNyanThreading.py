import threading
import subprocess
import logging
import time
import queue
import traceback
import os
import random
import bisect

from . import aNyanData
from . import aNyanExceptions
from . import aNyanGlobals
from . import aNyanGlobals

NEXT_THREAD_CLEAROUT = 0

THREADS_TO_THREAD_INFO = {}

THREAD_INFO_LOCK = threading.Lock()


def die_if_thread_is_shutting_down():

    if is_thread_shutting_down():

        raise aNyanExceptions.Shutdown_Exception("Thread is shutting down!")


def clear_out_dead_threads():

    with THREAD_INFO_LOCK:

        for thread in list(THREADS_TO_THREAD_INFO.keys()):

            if not thread.is_alive():

                del THREADS_TO_THREAD_INFO[thread]


def get_thread_info(thread: threading.Thread = None):

    global NEXT_THREAD_CLEAROUT

    if aNyanData.time_has_passed(NEXT_THREAD_CLEAROUT):

        clear_out_dead_threads()

        NEXT_THREAD_CLEAROUT = aNyanData.time_now() + 600

    if thread is None:

        thread = threading.current_thread()

    with THREAD_INFO_LOCK:

        if thread not in THREADS_TO_THREAD_INFO:

            THREADS_TO_THREAD_INFO[thread] = {"shutting_down": False}

        return THREADS_TO_THREAD_INFO[thread]


def is_thread_shutting_down():

    if isinstance(threading.current_thread(), Daemon):

        if aNyanGlobals.started_shutdown:

            return True

    thread_info = get_thread_info()

    return thread_info["shutting_down"]


def shutdown_thread(thread: threading.Thread):

    thread_info = get_thread_info(thread)

    thread_info["shutting_down"] = True


def Subprocess_Communicate(process: subprocess.Popen):
    def do_test():

        if aNyanGlobals.started_shutdown:

            try:

                process.kill()

            except:

                pass

            raise aNyanExceptions.Shutdown_Exception("Application is shutting down!")

    do_test()

    while True:

        try:

            return process.communicate(timeout=10)

        except subprocess.TimeoutExpired:

            do_test()


class Daemon(threading.Thread):
    def __init__(self, controller, name: str):

        threading.Thread.__init__(self, name=name)

        self._controller = controller
        self._name = name

        self._event = threading.Event()

    def _do_pre_call(self):

        if aNyanGlobals.daemon_report_mode:

            logging.info(self._name + " doing a job.")

    def get_current_job_summary(self):

        return "unknown job"

    def get_name(self):

        return self._name

    def shutdown(self):

        shutdown_thread(self)

        self.wake()

    def wake(self):

        self._event.set()


class Daemon_Worker(Daemon):

    """
    A Daemon Worker thread

    This auto-starting thread repeats the given callack every period of seconds passed

    The callback should accept 1 argument for which is the controller of the thread
    """

    def __init__(
        self,
        controller,
        name: str,
        callable,
        topics: list = None,
        period_seconds: int = 3600,
        init_wait: int = 3,
        pre_call_wait: int = 0,
    ):

        if topics is None:

            topics = []

        Daemon.__init__(self, controller, name)

        self._callable = callable
        self._topics = topics
        self._period = period_seconds
        self._init_wait = init_wait
        self._pre_call_wait = pre_call_wait

        for topic in topics:

            self._controller.sub(self, "set", topic)

        self.start()

    def _can_start(self):

        return self._controller_is_ok_with_it()

    def _controller_is_ok_with_it(self):

        return True

    def _do_await(self, wait_time, event_can_wake=True):

        time_to_start = aNyanData.time_now() + wait_time

        while not aNyanData.time_has_passed(time_to_start):

            if event_can_wake:

                event_was_set = self._event.wait(1.0)

                if event_was_set:

                    self._event.clear()

                    return
            else:

                time.sleep(1.0)

            die_if_thread_is_shutting_down()

    def _wait_until_can_start(self):

        while not self._can_start():

            time.sleep(1.0)

            die_if_thread_is_shutting_down()

    def get_current_job_summary(self):

        return self._callable

    def set(self, *args, **kwargs):

        self._event.set()

    def run(self):

        try:

            self._do_await(self._init_wait)

            while True:

                die_if_thread_is_shutting_down()

                self._do_await(self._pre_call_wait, event_can_wake=False)

                die_if_thread_is_shutting_down()

                self._wait_until_can_start()

                die_if_thread_is_shutting_down()

                self._do_pre_call()

                try:

                    self._callable(self._controller)

                except aNyanExceptions.Shutdown_Exception:

                    return

                except Exception as e:

                    logging.error("Daemon " + self._name + " encountered an exception:")

                    aNyanData.print_exception(e)

                self._do_await(self._period)

        except aNyanExceptions.Shutdown_Exception:

            return


# Big stuff like DB maintenance that we don't want to run while other important stuff is going on,
# like user interaction or vidya on another process
class Daemon_Background_Worker(Daemon_Worker):
    def _controller_is_ok_with_it(self):

        return self._controller.good_time_to_start_background_work()


# Big stuff that we want to run when the user sees,
# but not at the expense of something else, like laggy session load
class Daemon_Foreground_Worker(Daemon_Worker):
    def _controller_is_ok_with_it(self):

        return self._controller.good_time_to_start_background_work()


class Threadcall_To_Thread(Daemon):
    """
    A Daemon Worker thread.

    This thread must be started manually.

    This thread waits until a given callback is recieved before performing any jobs.
    """

    def __init__(self, controller, name):

        Daemon.__init__(self, controller, name)

        self._callable = None

        self._queue = queue.Queue()

        self._currently_working = True  # start off true so new threads aren't used twice by two quick successive calls

    def currently_working(self):

        return self._currently_working

    def get_current_job_summary(self):

        return self._callable

    def put(self, callable, *args, **kwargs):

        self._currently_working = True

        self._queue.put((callable, args, kwargs))

        self._event.set()

    def run(self):

        try:

            while True:

                while self._queue.empty():

                    die_if_thread_is_shutting_down()

                    self._event.wait(10.0)

                    self._event.clear()

                die_if_thread_is_shutting_down()

                try:

                    try:

                        (callable, args, kwargs) = self._queue.get(1.0)

                    except queue.Empty:

                        # https://github.com/hydrusnetwork/hydrus/issues/750
                        # this shouldn't happen, but...
                        # even if we assume we'll never get this, we don't want to make a business of hanging forever on things

                        continue

                    self._do_pre_call()

                    self._callable = (callable, args, kwargs)

                    callable(*args, **kwargs)

                    self._callable = None

                    del callable

                except aNyanExceptions.Shutdown_Exception:

                    return

                except Exception as e:

                    aNyanData.print_exception(e)

                finally:

                    self._currently_working = False

                time.sleep(0.00001)

        except aNyanExceptions.Shutdown_Exception:

            return


class Job_Scheduler(threading.Thread):
    def __init__(self, controller):

        threading.Thread.__init__(self, name="Job Scheduler")

        self._controller = controller

        self._waiting: list[Schedulable_Job] = []

        self._waiting_lock = threading.Lock()

        self._new_job_arrived = threading.Event()

        self._current_job: Schedulable_Job = None

        self._cancel_filter_needed = threading.Event()
        self._sort_needed = threading.Event()

        self._controller.sub(self, "shutdown", "shutdown")

    def _filter_cancelled(self):

        with self._waiting_lock:

            self._waiting = [job for job in self._waiting if not job.is_cancelled()]

    def _get_loop_wait_time(self):

        with self._waiting_lock:

            if len(self._waiting) == 0:

                return 0.2

            next_job = self._waiting[0]

        time_delta_until_due = next_job.get_time_delta_until_due()

        return min(1.0, time_delta_until_due)

    def _no_work_to_start(self):

        with self._waiting_lock:

            if len(self._waiting) == 0:

                return True

            next_job = self._waiting[0]

        if next_job.is_due():

            return False

        else:

            return True

    def _sort_waiting(self):

        # sort the waiting jobs in ascending order of expected work time

        with self._waiting_lock:  # this uses __lt__ to sort

            self._waiting.sort()

    def _start_work(self):

        jobs_started = 0

        while True:

            with self._waiting_lock:

                if len(self._waiting) == 0:

                    break

                if jobs_started >= 10:  # try to avoid spikes

                    break

                next_job = self._waiting[0]

                if not next_job.is_due():

                    # front is not due, so nor is the rest of the list
                    break

                next_job = self._waiting.pop(0)

            if next_job.is_cancelled():

                continue

            if next_job.slot_ok():

                # important this happens outside of the waiting lock lmao!
                next_job.start_work()

                jobs_started += 1

            else:

                # delay is automatically set by SlotOK

                with self._waiting_lock:

                    bisect.insort(self._waiting, next_job)

    def add_job(self, job):

        with self._waiting_lock:

            bisect.insort(self._waiting, job)

        self._new_job_arrived.set()

    def clear_out_dead(self):

        with self._waiting_lock:

            self._waiting = [job for job in self._waiting if not job.IsDead()]

    def get_name(self):

        return "Job Scheduler"

    def get_current_job_summary(self):

        with self._waiting_lock:

            return aNyanData.to_human_int(len(self._waiting)) + " jobs"

    def get_jobs(self):

        with self._waiting_lock:

            return list(self._waiting)

    def get_pretty_job_summary(self):

        with self._waiting_lock:

            num_jobs = len(self._waiting)

            job_lines = [repr(job) for job in self._waiting]

            lines = [aNyanData.to_human_int(num_jobs) + " jobs:"] + job_lines

            text = os.linesep.join(lines)

            return text

    def job_cancelled(self):

        self._cancel_filter_needed.set()

    def shutdown(self):

        shutdown_thread(self)

        self._new_job_arrived.set()

    def work_times_have_changed(self):

        self._sort_needed.set()

    def run(self):

        while True:

            try:

                while self._no_work_to_start():

                    if is_thread_shutting_down():

                        return

                    if self._cancel_filter_needed.is_set():

                        self._filter_cancelled()

                        self._cancel_filter_needed.clear()

                    if self._sort_needed.is_set():

                        self._sort_waiting()

                        self._sort_needed.clear()

                        continue  # if some work is now due, let's do it!

                    wait_time = self._get_loop_wait_time()

                    self._new_job_arrived.wait(wait_time)

                    self._new_job_arrived.clear()

                self._start_work()

            except aNyanExceptions.Shutdown_Exception:

                return

            except Exception as e:

                logging.error(traceback.format_exc())

                aNyanData.print_exception(e)

            time.sleep(0.00001)


class Schedulable_Job(object):

    PRETTY_CLASS_NAME = "job base"

    def __init__(self, controller, scheduler: Job_Scheduler, initial_delay, work_callable):

        self._controller = controller
        self._scheduler = scheduler
        self._work_callable = work_callable

        self._should_delay_on_wakeup = False

        self._next_work_time = aNyanData.time_now_float() + initial_delay

        self._thread_slot_type = None

        self._work_lock = threading.Lock()

        self._currently_working = threading.Event()
        self._is_cancelled = threading.Event()

    def __lt__(self, other):  # for the scheduler to do bisect.insort noice

        return self._next_work_time < other._next_work_time

    def __repr__(self):

        return "{}: {} {}".format(self.PRETTY_CLASS_NAME, self.get_pretty_job(), self.get_due_string())

    def _boot_worker(self):

        self._controller.CallToThread(self.Work)

    def cancel(self):

        self._is_cancelled.set()

        self._scheduler.job_cancelled()

    def currently_working(self):

        return self._currently_working.is_set()

    def get_due_string(self):

        due_delta = self._next_work_time - aNyanData.time_now_float()

        due_string = aNyanData.time_delta_to_pretty_time_delta(due_delta)

        if due_delta < 0:

            due_string = "was due {} ago".format(due_string)

        else:

            due_string = "due in {}".format(due_string)

        return due_string

    def get_next_work_time(self):

        return self._next_work_time

    def get_pretty_job(self):

        return repr(self._work_callable)

    def get_time_delta_until_due(self):

        return aNyanData.time_delta_until_time_float(self._next_work_time)

    def is_cancelled(self):

        return self._is_cancelled.is_set()

    def is_dead(self):

        return False

    def is_due(self):

        return aNyanData.time_has_passed_float(self._next_work_time)

    def pub_sub_wake(self, *args, **kwargs):

        self.wake()

    def set_thread_slot_type(self, thread_type):

        self._thread_slot_type = thread_type

    def ShouldDelayOnWakeup(self, value):

        self._should_delay_on_wakeup = value

    def slot_ok(self):

        if self._thread_slot_type is not None:

            if aNyanGlobals.controller.acquire_thread_slot(self._thread_slot_type):

                return True

            else:

                self._next_work_time = aNyanData.time_now_float() + 10 + random.random()

                return False

        return True

    def start_work(self):

        if self._is_cancelled.is_set():

            return

        self._currently_working.set()

        self._boot_worker()

    def wake(self, next_work_time=None):

        if next_work_time is None:

            next_work_time = aNyanData.time_now_float()

        self._next_work_time = next_work_time

        self._scheduler.work_times_have_changed()

    def wake_on_pub_sub(self, topic):

        aNyanGlobals.controller.sub(self, "PubSubWake", topic)

    def work(self):

        try:

            if self._should_delay_on_wakeup:

                while aNyanGlobals.controller.just_woke_from_sleep():

                    if is_thread_shutting_down():

                        return

                    time.sleep(1)

            with self._work_lock:

                self._work_callable()

        finally:

            if self._thread_slot_type is not None:

                aNyanGlobals.controller.release_thread_slot(self._thread_slot_type)

            self._currently_working.clear()


class Single_Job(Schedulable_Job):

    PRETTY_CLASS_NAME = "single job"

    def __init__(self, controller, scheduler: Job_Scheduler, initial_delay, work_callable):

        Schedulable_Job.__init__(self, controller, scheduler, initial_delay, work_callable)

        self._work_complete = threading.Event()

    def is_work_complete(self):

        return self._work_complete.is_set()

    def work(self):

        Schedulable_Job.work(self)

        self._work_complete.set()


class Repeating_Job(Schedulable_Job):

    PRETTY_CLASS_NAME = "repeating job"

    def __init__(self, controller, scheduler: Job_Scheduler, initial_delay, period, work_callable):

        Schedulable_Job.__init__(self, controller, scheduler, initial_delay, work_callable)

        self._period = period

        self._stop_repeating = threading.Event()

    def cancel(self):

        Schedulable_Job.cancel(self)

        self._stop_repeating.set()

    def delay(self, delay):

        self._next_work_time = aNyanData.time_now_float() + delay

        self._scheduler.work_times_have_changed()

    def is_repeating_work_finished(self):

        return self._stop_repeating.is_set()

    def start_work(self):

        if self._stop_repeating.is_set():

            return

        Schedulable_Job.start_work(self)

    def work(self):

        Schedulable_Job.work(self)

        if not self._stop_repeating.is_set():

            self._next_work_time = aNyanData.time_now_float() + self._period

            self._scheduler.add_job(self)
