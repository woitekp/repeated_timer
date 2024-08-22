if __name__ == '__main__':

    from multiprocessing import Event
    import signal
    import time

    from repeated_timer import ExampleTask1, repeated_timer_handler, ExampleTask2
    from utils import run_process 

    def sigint_handler(signum, frame):  # signum (signal number), frame (stack frame) are passed to handler by default
        """Set stop event""" 
                
        print('Please wait for the program end...')
        if not stop_event.is_set():
            stop_event.set()
            
        # prevent user from sending sigint too many times
        # as in extreme case (if KeyboardInterrupt is sent continuously)
        # it may cause a crash
        signal.signal(signal.SIGINT, lambda x, y: None)  # do nothing on interrupt signal
        time.sleep(.1)
        signal.signal(signal.SIGINT, sigint_handler)  # let user see the message again

    stop_event = Event()
    signal.signal(signal.SIGINT, sigint_handler)  # handle interrupt signal
    
    # run_process(repeated_timer_handler, ExampleTask1, stop_event, interval=5)
    run_process(repeated_timer_handler, ExampleTask2, stop_event, interval=10)
    
    while not stop_event.is_set():
        time.sleep(.1)
