from abc import ABC, abstractmethod
import logging
import multiprocessing
from typing import Optional

class MultiprocessingWorker(ABC):
    def __init__(self, worker_name: Optional[str] = None, asThread: bool = False) -> None:
        self._process = None
        self._inputQueue = multiprocessing.Queue()
        self._outputQueue = multiprocessing.Queue()
        self._lock = multiprocessing.Lock()
        self._running = multiprocessing.Event()
        self._worker_name = worker_name if not (worker_name is None or worker_name == "") else str(hex(id(self)))

    def __del__(self) -> None:
        self.clear_queues()
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
                logging.error(f"Error in worker {self._worker_name} loop: {e}")

    def isRunning(self) -> bool:
        with self._lock:
            return self._process is not None and self._process.is_alive()

    @abstractmethod
    def worker_loop_function(self) -> None:
        pass

    def start(self) -> bool:
        with self._lock:
            if self._process is None or not self._process.is_alive():
                self._process = multiprocessing.Process(target=self.__worker_loop)
                self._running.set()
                self.clear_queues()
                self._process.start()
                return True
            return False

    def stop(self) -> bool:
        with self._lock:
            if self._process is not None and self._process.is_alive():
                self._running.clear()
                self._process.join()
                self._process = None
                self.clear_queues()
                return True
            return False