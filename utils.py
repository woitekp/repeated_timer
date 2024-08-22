from functools import wraps
from multiprocessing import Process
from threading import Thread


def run_process(func, *args, **kwargs):
    proc = Process(target=func, args=args, kwargs=kwargs)
    proc.start()


def threaded(func):
    """wrapper for making func run in a new thread. Returns Thread object"""

    # wraps updates the wrapper function to look like wrapped function
    # by copying attributes such as __name__, __doc__ (the docstring), etc.
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
