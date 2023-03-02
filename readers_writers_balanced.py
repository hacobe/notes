"""A solution to the Readers-Writers problem that balances concerns of readers and writers.

Sources:
* https://github.com/PacktPublishing/Mastering-Concurrency-in-Python/blob/master/Chapter13/example3.py
* https://cs.stackexchange.com/questions/54466/confusion-in-the-solution-to-first-readers-writers-synchronization
* https://en.wikipedia.org/wiki/Readers%E2%80%93writers_problem#Third_readers%E2%80%93writers_problem
* https://stackoverflow.com/questions/8158442/fair-semaphore-in-python
"""
import threading

def writer():
    global service
    global write_lock

    while True:
        with service:
            write_lock.acquire()

        print(f'Writing being done by {threading.current_thread().name}.')

        write_lock.release()

def reader():
    global service
    global reader_count_lock
    global reader_count
    global write_lock

    while True:
        with service:
            with reader_count_lock:
                reader_count += 1
                if reader_count == 1:
                    write_lock.acquire()

        print(f'Reading being done by {threading.current_thread().name}:')

        with reader_count_lock:
            reader_count -= 1
            if reader_count == 0:
                write_lock.release()

if __name__ == "__main__":
    global reader_count
    global reader_count_lock
    global write_lock
    global service

    reader_count = 0
    reader_count_lock = threading.Lock()
    write_lock = threading.Lock()

    # I think if multiple threads are waiting on the service lock and it gets released,
    # a more or less random waiting thread will grab it (which one is determined by the OS).
    # It might be better to have a "fair" lock. I don't think Python has one implemented
    # out of the box.
    service = threading.Lock()

    reader_threads = [threading.Thread(target=reader) for i in range(3)]
    writer_threads = [threading.Thread(target=writer) for i in range(2)]
    threads = reader_threads + writer_threads

    for thread in threads:
        thread.start()