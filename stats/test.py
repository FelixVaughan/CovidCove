import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import time


lst = []
def test_func():
    id = threading.current_thread().ident
    lst.append(id)


num_threads = multiprocessing.cpu_count() * 2
pool = ThreadPoolExecutor(num_threads)
for i in range(1000):
    future = pool.submit(test_func)

print(set(lst))