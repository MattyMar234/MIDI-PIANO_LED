from abc import ABC, abstractmethod
import logging
import multiprocessing

class MultiprocessingWorker(ABC):
    def __init__(self):
        print("Initializing MultiprocessingWorker")
        self._process = None
        self._inputQueue = multiprocessing.Queue()
        self._outputQueue = multiprocessing.Queue()
        self._lock = multiprocessing.Lock()
        self._running = multiprocessing.Event()

    def __del__(self) -> None:
        self.stop()

    def clear_queues(self) -> None:
        while self._inputQueue.qsize() > 0:
            self._inputQueue.get()
        while self._outputQueue.qsize() > 0:
            self._outputQueue.get()

    def __worker_loop(self) -> None:
        while self._running.is_set():
            try:
                self.worker_loop_function()
            except Exception as e:
                logging.error(f"Error in worker loop: {e}")



    @abstractmethod
    def worker_loop_function(self) -> None:
        pass

    def start(self) -> bool:
        if self._process is None or not self._process.is_alive():
            self._process = multiprocessing.Process(target=self.__worker_loop)
            self._running.set()
            self.clear_queues()
            self._process.start()
            return True
        return False

    def stop(self) -> bool:
        if self._process is not None and self._process.is_alive():
            self._running.clear()
            self._process.join()
            self._process = None
            self.clear_queues()
            return True
        return False