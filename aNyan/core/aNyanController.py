import threading
import collections
import random
import time
import sys
import os
import traceback
from typing import Callable

from . import aNyanConstants
from . import aNyanGlobals
from . import aNyanData
from . import aNyanThreading
from . import aNyanExceptions
from . import aNyanTemp
from . import aNyanPaths
from . import aNyanPubSub
from . import aNyanDB
from . import aNyanLogging as logging


class Nyan_Controller(object):
    def __init__(self, db_dir):

        aNyanGlobals.controller = self

        self._name: str = aNyanConstants.BRAND

        self._last_shutdown_was_bad = False
        self._i_own_running_file: bool = False

        self.db_dir: str = db_dir

        self.db: aNyanDB.Nyan_DB = None

        self._pubsub: aNyanPubSub.Nyan_PubSub = aNyanPubSub.Nyan_PubSub()
        self._daemon_jobs: dict[str, aNyanThreading.Schedulable_Job] = {}
        self._caches = {}
        self._managers = {}

        self._fast_job_scheduler = None
        self._slow_job_scheduler = None

        self._thread_slots: dict[str, tuple[int, int]] = {}

        self._thread_slots["misc"] = (0, 10)

        self._thread_slot_lock = threading.Lock()

        self._call_to_threads: list[aNyanThreading.Thread_Call_To_Thread] = []
        self._long_running_call_to_threads: list[aNyanThreading.Thread_Call_To_Thread] = []

        self._thread_pool_busy_status_text = ""
        self._thread_pool_busy_status_text_new_check_time = 0

        self._call_to_thread_lock = threading.Lock()

        self._timestamps_lock = threading.Lock()

        self._timestamps: collections.defaultdict[str, int] = collections.defaultdict(lambda: 0)

        self._timestamps["boot"] = aNyanData.time_now()

        self._timestamps["last_sleep_check"] = aNyanData.time_now()

        self._sleep_lock = threading.Lock()

        self._just_woke_from_sleep = False

        self._system_busy = False

        self._doing_fast_exit = False

    def _get_call_to_thread(self):

        with self._call_to_thread_lock:

            for call_to_thread in self._call_to_threads:

                if not call_to_thread.is_currently_working():

                    return call_to_thread

            # all the threads in the pool are currently busy

            calling_from_the_thread_pool = threading.current_thread() in self._call_to_threads

            if calling_from_the_thread_pool or len(self._call_to_threads) < 200:

                call_to_thread = aNyanThreading.Thread_Call_To_Thread(self, "CallToThread")

                self._call_to_threads.append(call_to_thread)

                call_to_thread.start()

            else:

                call_to_thread = random.choice(self._call_to_threads)

            return call_to_thread

    def _get_call_to_threadlong_running(self):

        with self._call_to_thread_lock:

            for call_to_thread in self._long_running_call_to_threads:

                if not call_to_thread.is_currently_working():

                    return call_to_thread

            call_to_thread = aNyanThreading.Thread_Call_To_Thread(self, "CallToThreadLongRunning")

            self._long_running_call_to_threads.append(call_to_thread)

            call_to_thread.start()

            return call_to_thread

    def _get_appropriate_job_scheduler(self, time_delta):

        if time_delta <= 1.0:

            return self._fast_job_scheduler

        else:

            return self._slow_job_scheduler

    def _get_wake_delay_period(self):

        return 15

    def _init_temp_dir(self):

        self.temp_dir = aNyanTemp.get_temp_dir()

    def _maintain_call_to_threads(self):

        # we don't really want to hang on to threads that are done as event.wait() has a bit of idle cpu
        # so, any that are in the pools that aren't doing anything can be killed and sent to garbage

        with self._call_to_thread_lock:

            def filter_call_to_threads(t: aNyanThreading.Thread_Call_To_Thread):

                if t.is_currently_working():

                    return True

                else:

                    t.shutdown()

                    return False

            self._call_to_threads = list(filter(filter_call_to_threads, self._call_to_threads))

            self._long_running_call_to_threads = list(filter(filter_call_to_threads, self._long_running_call_to_threads))

    def _read(self, action: str, *args, **kwargs):

        return self.db.read(action, *args, **kwargs)

    def _write(self, action, synchronous, *args, **kwargs):

        return self.db.write(action, synchronous, *args, **kwargs)

    def _show_just_woke_to_user(self):

        logging.info("Just woke from sleep.")

    def _shutdown_daemons(self):

        for job in self._daemon_jobs.values():

            job.cancel()

        started = aNyanData.time_now()

        while True in (daemon_job.is_currently_working() for daemon_job in self._daemon_jobs.values()):

            self._report_shutdown_daemons_status()

            time.sleep(0.1)

            if aNyanData.time_has_passed(started + 30):

                break

        self._daemon_jobs = {}

    def _init_db(self):

        raise NotImplementedError("You must override this this function!")

    def _publish_shutdown_subtext(self, text):

        pass

    def _report_shutdown_daemons_status(self):

        pass

    def pub(self, topic: str, *args, **kwargs):

        if aNyanGlobals.model_shutdown:

            self._pubsub.pubimmediately_here(topic, *args, **kwargs)

        else:

            self._pubsub.pub(topic, *args, **kwargs)

    def pubimmediate(self, topic: str, *args, **kwargs):

        self._pubsub.pubimmediately_here(topic, *args, **kwargs)

    def sub(self, object: object, method_name: str, topic: str):

        self._pubsub.sub(object, method_name, topic)

    def can_acquire_thread_slot(self, thread_type: str) -> bool:

        with self._thread_slot_lock:

            if thread_type not in self._thread_slots:

                return True  # assume no max if no max set

            (current_threads, max_threads) = self._thread_slots[thread_type]

            if current_threads < max_threads:

                self._thread_slots[thread_type] = (current_threads + 1, max_threads)

                return True

            else:

                return False

    def call_later(self, initial_delay_seconds: float, func: Callable, *args, **kwargs) -> aNyanThreading.Single_Job:

        job_scheduler = self._get_appropriate_job_scheduler(initial_delay_seconds)

        call = aNyanData.Call(func, *args, **kwargs)

        job = aNyanThreading.Single_Job(self, job_scheduler, initial_delay_seconds, call)

        job_scheduler.add_job(job)

        return job

    def call_repeating(
        self, initial_delay_seconds: float, period: float, func: Callable, *args, **kwargs
    ) -> aNyanThreading.Repeating_Job:

        job_scheduler = self._get_appropriate_job_scheduler(period)

        call = aNyanData.Call(func, *args, **kwargs)

        job = aNyanThreading.Repeating_Job(self, job_scheduler, initial_delay_seconds, period, call)

        job_scheduler.add_job(job)

        return job

    def call_to_thread(self, callable: Callable, *args, **kwargs):

        if aNyanGlobals.callto_report_mode:

            what_to_report = [callable]

            if len(args) > 0:

                what_to_report.append(args)

            if len(kwargs) > 0:

                what_to_report.append(kwargs)

            logging.info(tuple(what_to_report))

        call_to_thread = self._get_call_to_thread()

        call_to_thread.put(callable, *args, **kwargs)

    def call_to_thread_long_running(self, callable: Callable, *args, **kwargs):

        if aNyanGlobals.callto_report_mode:

            what_to_report = [callable]

            if len(args) > 0:

                what_to_report.append(args)

            if len(kwargs) > 0:

                what_to_report.append(kwargs)

            logging.info(tuple(what_to_report))

        call_to_thread = self._get_call_to_threadlong_running()

        call_to_thread.put(callable, *args, **kwargs)

    def clean_running_file(self):

        if self._i_own_running_file:

            aNyanData.clean_running_file(self.db_dir, self._name)

    def clear_caches(self):

        for cache in list(self._caches.values()):
            cache.Clear()

    def is_currently_idle(self):

        return True

    def is_currently_pub_subbing(self):

        return self._pubsub.work_to_do() or self._pubsub.doing_work()

    def is_db_currently_doing_job(self):

        return (self.db is not None) and self.db.is_currently_doing_job()

    def is_doing_fast_exit(self) -> bool:

        return self._doing_fast_exit

    def is_first_start(self):

        return (self.db is not None) and self.db.is_first_start()

    def is_good_time_to_start_background_work(self):

        return self.is_currently_idle() and not (self.just_woke_from_sleep() or self.is_system_busy())

    def is_good_time_to_start_foreground_work(self):

        return not self.just_woke_from_sleep()

    def is_system_busy(self):

        return self._system_busy

    def last_shutdown_was_bad(self):

        return self._last_shutdown_was_bad

    def just_woke_from_sleep(self):

        self.sleep_check()

        return self._just_woke_from_sleep

    def get_boot_time(self):

        return self.get_timestamp("boot")

    def get_db_dir(self):

        return self.db_dir

    def get_db_status(self):

        return self.db.get_status()

    def get_cache(self, name):

        return self._caches[name]

    def get_job_scheduler_snapshot(self, scheduler_name):

        if scheduler_name == "fast":

            scheduler = self._fast_job_scheduler

        else:

            scheduler = self._slow_job_scheduler

        return scheduler.get_jobs()

    def get_manager(self, name):

        return self._managers[name]

    def get_thread_pool_busy_status(self):

        if aNyanData.time_has_passed(self._thread_pool_busy_status_text_new_check_time):

            with self._call_to_thread_lock:

                num_threads = sum(1 for t in self._call_to_threads if t.is_currently_working())

            if num_threads < 4:

                self._thread_pool_busy_status_text = ""

            elif num_threads < 10:

                self._thread_pool_busy_status_text = "working"

            elif num_threads < 20:

                self._thread_pool_busy_status_text = "busy"

            else:

                self._thread_pool_busy_status_text = "very busy!"

            self._thread_pool_busy_status_text_new_check_time = aNyanData.time_now() + 10

        return self._thread_pool_busy_status_text

    def get_threads_snapshot(self):

        threads = []

        threads.extend(self._call_to_threads)
        threads.extend(self._long_running_call_to_threads)

        threads.append(self._slow_job_scheduler)
        threads.append(self._fast_job_scheduler)

        return threads

    def get_timestamp(self, name: str) -> int:

        with self._timestamps_lock:

            return self._timestamps[name]

    def init_model(self):
        try:

            self._init_temp_dir()

        except:

            logging.warning("Failed to initialise temp folder.")

        self._fast_job_scheduler = aNyanThreading.Job_Scheduler(self)
        self._slow_job_scheduler = aNyanThreading.Job_Scheduler(self)

        self._fast_job_scheduler.start()
        self._slow_job_scheduler.start()

        self.db = self._init_db()

    def daemon_pubsub(self):

        while not aNyanGlobals.model_shutdown:

            if self._pubsub.work_to_do():

                try:

                    self._pubsub.process()

                except Exception as e:

                    aNyanData.print_exception(e)

            else:

                self._pubsub.wait_on_pub()

    def init_view(self):

        job = self.call_repeating(60.0, 300.0, self.maintain_db, maintenance_mode=aNyanConstants.MAINTENANCE_IDLE)
        job.wake_on_pub_sub("wake_idle_workers")
        job.should_delay_on_wakeup(True)
        self._daemon_jobs["maintain_db"] = job

        job = self.call_repeating(0.0, 15.0, self.sleep_check)
        self._daemon_jobs["sleep_check"] = job

        job = self.call_repeating(10.0, 60.0, self.maintain_memory_fast)
        self._daemon_jobs["maintain_memory_fast"] = job

        job = self.call_repeating(10.0, 300.0, self.maintain_memory_slow)
        self._daemon_jobs["maintain_memory_slow"] = job

        self.call_to_thread_long_running(self.daemon_pubsub)
        # upnp_services = self._GetUPnPServices()

        # self.services_upnp_manager = HydrusNATPunch.ServicesUPnPManager(upnp_services)

        # job = self.call_repeating(10.0, 43200.0, self.services_upnp_manager.RefreshUPnP)

        # self._daemon_jobs["services_upnp"] = job

    def maintain_db(self, maintenance_mode=aNyanConstants.MAINTENANCE_IDLE, stop_time=None):

        pass

    def maintain_memory_fast(self):

        sys.stdout.flush()
        sys.stderr.flush()

        self.pub("memory_maintenance_pulse")

        self._fast_job_scheduler.clear_out_dead()
        self._slow_job_scheduler.clear_out_dead()

    def maintain_memory_slow(self):

        aNyanTemp.clean_up_old_temp_paths()

        self._maintain_call_to_threads()

    def print_profile(self, summary: str, profile_text: str = None):

        pretty_timestamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(aNyanGlobals.profile_start_time))

        profile_log_filename = "{} profile - {}.log".format(self._name, pretty_timestamp)

        profile_log_path = os.path.join(self.db_dir, profile_log_filename)

        with open(profile_log_path, "a", encoding="utf-8") as f:

            prefix = time.strftime("%Y/%m/%d %H:%M:%S: ")

            f.write(prefix + summary)

            if profile_text is not None:

                f.write("\n\n")
                f.write(profile_text)

    def read(self, action: str, *args, **kwargs):

        return self._read(action, *args, **kwargs)

    def record_running_start(self):

        self._last_shutdown_was_bad = aNyanData.last_shutdown_was_bad(self.db_dir, self._name)

        self._i_own_running_file = True

        aNyanData.record_running_start(self.db_dir, self._name)

    def release_thread_slot(self, thread_type: str):

        with self._thread_slot_lock:

            if thread_type not in self._thread_slots:

                return

            (current_threads, max_threads) = self._thread_slots[thread_type]

            self._thread_slots[thread_type] = (current_threads - 1, max_threads)

    def report_data_used(self, num_bytes):

        pass

    def report_request_used(self):

        pass

    def reset_idle_timer(self):

        self.touch_timestamp("last_user_action")

    def set_doing_fast_exit(self, value: bool):

        self._doing_fast_exit = value

    def set_timestamp(self, name: str, value: int):

        with self._timestamps_lock:

            self._timestamps[name] = value

    def should_stop_this_work(self, maintenance_mode: int, stop_time=None):

        if maintenance_mode == aNyanConstants.MAINTENANCE_IDLE:

            return not self.is_currently_idle()

        if maintenance_mode == aNyanConstants.MAINTENANCE_SHUTDOWN:

            return not aNyanGlobals.do_idle_shutdown_work

        if stop_time is not None:

            return aNyanData.time_has_passed(stop_time)

        return False

    def shutdown_model(self):

        if self.db is not None:

            self.db.shutdown()

            while not self.db.is_loop_finished():

                self._publish_shutdown_subtext("waiting for db to finish up\u2026")

                time.sleep(0.1)

        if self._fast_job_scheduler is not None:

            self._fast_job_scheduler.shutdown()

            self._fast_job_scheduler = None

        if self._slow_job_scheduler is not None:

            self._slow_job_scheduler.shutdown()

            self._slow_job_scheduler = None

        if hasattr(self, "temp_dir"):

            aNyanPaths.delete_path(self.temp_dir)

        with self._call_to_thread_lock:

            for call_to_thread in self._call_to_threads:

                call_to_thread.shutdown()

            for long_running_call_to_thread in self._long_running_call_to_threads:

                long_running_call_to_thread.shutdown()

        aNyanGlobals.model_shutdown = True

        self._pubsub.wake()

    def shutdown_view(self):

        aNyanGlobals.view_shutdown = True

        self._shutdown_daemons()

    def shutdown_from_server(self):

        raise Exception("This hydrus application cannot be shut down from the server!")

    def sleep_check(self):

        with self._sleep_lock:

            # it has been way too long since this method last fired, so we've prob been asleep
            if aNyanData.time_has_passed(self.get_timestamp("last_sleep_check") + 60):

                self._just_woke_from_sleep = True

                # this will stop the background jobs from kicking in as soon as the grace period is over
                self.reset_idle_timer()

                wake_delay_period = self._get_wake_delay_period()

                # enough time for ethernet to get back online and all that
                self.set_timestamp("now_awake", aNyanData.time_now() + wake_delay_period)

                self._show_just_woke_to_user()

            elif self._just_woke_from_sleep and aNyanData.time_has_passed(self.get_timestamp("now_awake")):

                self._just_woke_from_sleep = False

            self.touch_timestamp("last_sleep_check")

    def simulate_wake_from_sleep_event(self):

        with self._sleep_lock:

            self.set_timestamp("last_sleep_check", aNyanData.time_now() - 3600)

        self.sleep_check()

    def touch_timestamp(self, name: str):

        with self._timestamps_lock:

            self._timestamps[name] = aNyanData.time_now()

    def wait_until_db_empty(self):

        while True:

            if aNyanGlobals.model_shutdown:

                raise aNyanExceptions.Shutdown_Exception("Application shutting down!")

            elif self.db.is_jobs_queue_empty() and not self.db.is_currently_doing_job():

                return

            else:

                time.sleep(0.00001)

    def wait_until_model_free(self):

        self.wait_until_pub_subs_empty()

        self.wait_until_db_empty()

    def wait_until_pub_subs_empty(self):

        while self.is_currently_pub_subbing():

            if aNyanGlobals.model_shutdown:

                raise aNyanExceptions.Shutdown_Exception("Application shutting down!")

            else:

                time.sleep(0.00001)

    def wake_daemon(self, name):

        if name in self._daemon_jobs:

            self._daemon_jobs[name].wake()

    def write(self, action: str, *args, **kwargs):

        return self._write(action, False, *args, **kwargs)

    def write_synchronous(self, action: str, *args, **kwargs):

        return self._write(action, True, *args, **kwargs)

    def boot_everything_base(self):

        # try:

        #     self.CheckAlreadyRunning()

        # except aNyanExceptions.Shutdown_Exception:

        #     logging.warning("Already running this controller instance!")
        #     return

        try:

            self.record_running_start()

            self.init_model()

            self.init_view()

            self._is_booted = True

        except (aNyanExceptions.DB_Credentials_Exception, aNyanExceptions.Shutdown_Exception) as e:

            logging.error(e)

            self.clean_running_file()

        except Exception as e:

            trace = traceback.format_exc()

            text = (
                "If the db crashed, another error may be written just above ^."
                + os.linesep
                + "A serious error occurred while trying to start the program. "
                + "The error will be shown next in a window. "
                + "More information may have been written to client.log."
                + os.linesep * 2
                + trace
            )

            logging.error(text)

            if "malformed" in trace:

                hell_message = (
                    "Looking at it, it looks like your database may be malformed! "
                    + "This is a serious error. "
                    + 'Please check "/install_dir/db/help my db is broke.txt" as soon as you can for the next steps. '
                    + "The specific error will now follow."
                )

                logging.error(hell_message)

    def exit_everything_base(self):

        try:

            aNyanGlobals.started_shutdown = True

            self.shutdown_view()

            self.shutdown_model()

            self.clean_running_file()

        except (aNyanExceptions.DB_Credentials_Exception, aNyanExceptions.Shutdown_Exception):

            pass

        except Exception as e:

            aNyanData.print_exception(e)

        finally:

            self._program_is_shut_down = True
