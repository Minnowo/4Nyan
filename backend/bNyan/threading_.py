import threading 


from . import exceptions
from . import bn_logging
from . import constants_


_threads = {

}

lock = threading.Lock()

LOGGER = bn_logging.get_logger(constants_.BNYAN_THREADS[0], constants_.BNYAN_THREADS[1])

class Worker_Queue():

    """ a thread that calls the given callback passing data from a queue, callbacks should take care of errors """

    def __init__(self, function) -> None:
        
        self.dead = False 
        self.alive = True 
        self.is_working = False 
        self.__items = []
        self.__callbacks = []

        self.__callback = function

        self.__signal = threading.Event()
        self.__thread = threading.Thread(target=self.__worker_thread)
        self.__thread.start()

    def update_callback(self, callback):
        
        self.callback = callback 
   
    def enqueue_callback(self, item, callback):

        self.__callbacks.append(callback)
        self.__items.append(item)
        self.__signal.set()

    def enqueue(self, item):
        # enqueue the item and set the flag -> True 
        self.__callbacks.append(self.__callback)
        self.__items.append(item)
        self.__signal.set()

    def __worker_thread(self):
        
        # keep thread waiting
        while True:
            
            # if there are items in the queue
            # process until the queue is empty 
            if self.__items:
                # invoke the callback given by the user and return their item 
                self.is_working = True 

                callback = self.__callbacks.pop(0)
                item     = self.__items.pop(0)

                callback(item)


            else:
                # only kill thread after all items have been processed with
                if not self.alive:
                    break

                self.is_working = False 

                # reset the flag and pause the thread
                self.__signal.clear()
                self.__signal.wait()


    def cleanup(self):
        
        # allow while loop to end
        self.alive = False

        # trigger signal to end while loop
        self.__signal.set()

        # cleanup our thread 
        self.__thread.join()

        del self.__thread 
        del self.__signal 

        self.dead = True 

    def __del__(self):

        if not self.dead:
            self.cleanup()



def cleanup_all_threads():

    """ joins and deletes all worker threads """

    for (key, value) in _threads.items():

        LOGGER.info("Cleaning thread: {}".format(key))

        value.cleanup()
        
        del value 

    _threads.clear()



def spawn_worker_thread(thread_name : str, callback):

    """ creates a worker thread with the given name """

    LOGGER.info("Spawning worker thread: '{}'".format(thread_name))

    if thread_name in _threads:

        raise exceptions.Thread_Exists_Exception("Cannot create a thread with the name: '{}'".format(thread_name))

    worker = Worker_Queue(callback)

    _threads[thread_name] = worker 




def append_worker_data(thread_name : str, data, callback = None, is_single_use_callback = True ):

    """ adds data to an exsiting worker thread, if the callback is specified it will be used instead of the default """

    if thread_name not in _threads:
        raise exceptions.Thread_Does_Not_Exists_Exception("The thread '{}' is not in the pool".format(thread_name))

    worker = _threads[thread_name]

    if callback:

        if is_single_use_callback:
            worker.enqueue_callback(data, callback)
            return 

        worker.update_callback(callback)

    worker.enqueue(data)














