from abc import ABC, abstractmethod  # for requiring derived classes to override decorated methods
import logging
import signal
import threading
import time

from utils import threaded


def repeated_timer_handler(timer, stop_event, **kwargs):
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # ignore interrupt signal - wait for stop event
    timer = timer(**kwargs)
    while not stop_event.is_set():
        time.sleep(1)
    timer.stop()


class RepeatedTimer(ABC):
    """Base class for periodic tasks"""
    def __init__(self, interval=60, first_call_interval=0, start_on_init=True):
        self._interval = interval
        self._next_call_timestamp = None
        self._timer = None

        if start_on_init:
            self.start(first_call_interval)

    def stop(self):
        if self._timer is not None:
            # until cancel has effect (cannot cancel timer if function is already running)
            while self._timer.is_alive():
                self._timer.cancel()
                time.sleep(.1)
            self._timer = None

    def is_stopped(self):
        return self._timer is None

    def start(self, first_call_interval=0):  # by default set interval to zero -> run task immediately
        # run on startup only - prevent from executing if already scheduled
        if self._timer is None or not self._timer.is_alive():
            first_call_interval = max(first_call_interval, 0)
            self._next_call_timestamp = time.time() + first_call_interval  # absolute time of next self.task execution
            self._timer = threading.Timer(first_call_interval, self._run_and_schedule)
            self._timer.start()

    def _run_and_schedule(self):
        self._task()
        self._schedule()

    @abstractmethod
    def _task(self):
        """task to implement by derived class"""
        # abstractmethod has advantage over raising NotImplementedError
        # because it raises an explicit Exception immediately at instantiation time, not at method call time
    
    def _schedule(self):
        if self._timer is not None:
            self._determine_next_call_timestamp()
            # calculate timer interval by subtracting actual time from next_call absolute time
            interval = self._next_call_timestamp - time.time()
            self._timer = threading.Timer(interval, self._run_and_schedule)
            self._timer.start()

    def _determine_next_call_timestamp(self):
        self._next_call_timestamp += self._interval


class RepeatedTimerWithIntervalMonitor(RepeatedTimer):
    '''def __init__(self, interval=60, first_call_interval=0, start_on_init=True):
        self._interval = interval
        self._next_call_timestamp = None
        self._timer = None
        self._stopped = threading.Event()

        if start_on_init:
            self.start(first_call_interval)'''

    @threaded
    def start(self, first_call_interval=0):
        # by default set interval to zero -> run task immediately
        # run on startup only - prevent from executing if already scheduled
        if self._timer is None or not self._timer.is_alive():
            super().start(first_call_interval)
            self._interval_monitor()

    @threaded
    def _interval_monitor(self):
        time.sleep(5)
        while self._timer is not None:
            current_interval = self._get_interval()
            if self._interval != current_interval:
                print("Task interval has changed! Restarting")
                self.stop()
                next_call_interval = self._get_updated_next_call_interval(current_interval)
                self._interval = current_interval
                self.start(next_call_interval)
                return

            time.sleep(5)

    @abstractmethod
    def _get_interval(self):
        """function to implement by derived class"""

    def _get_updated_next_call_interval(self, current_interval):
        last_task_execution_timestamp = self._next_call_timestamp - self._interval
        next_call_timestamp = last_task_execution_timestamp + current_interval
        return next_call_timestamp - time.time()


class ExampleTask1(RepeatedTimer):
    def _task(self):
        print("Starting task 1. Time: {:.6f} (accuracy: {:.6f})".format(time.time(), self._next_call_timestamp - time.time()))
        time.sleep(3)  # simulate task taking some time...
        print("Task 1 finished\n")


from random import randint
TEST_INTERVALS = [3, 6]
class ExampleTask2(RepeatedTimerWithIntervalMonitor):
    def _task(self):
        print("Starting task 2. Time: {:.6f} (accuracy: {:.6f})".format(time.time(), self._next_call_timestamp - time.time()))
        time.sleep(1)  # simulate task taking some time...
        print("Task 2 finished\n")
    
    def _get_interval(self):
        return TEST_INTERVALS[randint(0, 1)]  # get one of two intervals  randomly