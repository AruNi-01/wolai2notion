import threading
import time
from concurrent.futures import ThreadPoolExecutor

start_idx, end_idx = 0, 99  # 处理 database_row 的起始 index 和结束 index


def test_thread_pool():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=8) as t:
        futures = []
        for idx in range(100):
            if idx < start_idx:
                continue
            if idx > end_idx:
                break

            future = t.submit(block_handle, idx)
            futures.append(future)

        for future in futures:
            result = future.result()     # 一直阻塞，直到执行完毕获取到 future
            print(f'idx: {result}, len(wolai.rows): 100')

    # 等待所有子线程执行完毕
    t.shutdown(wait=True)
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Total time: {total_time} seconds')


def block_handle(block_id):
    print(f'============== thread: {threading.current_thread().name}, block_id: {block_id}')
    time.sleep(3)
    return block_id + 1


if __name__ == '__main__':
    test_thread_pool()
