import threading
import queue
import time

def producer(q):
    for i in range(5):
        q.put(i)
        print(f'Produced {i}')
        time.sleep(1)

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f'Consumed {item}')
        q.task_done()

q = queue.Queue()
t1 = threading.Thread(target=producer, args=(q,))
t2 = threading.Thread(target=consumer, args=(q,))

t1.start()
t2.start()

t1.join()
q.put(None)  # 通知消费者线程结束
t2.join()
