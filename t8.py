import collections
import heapq
import itertools
import random
import time


async def one_task():
    """一个任务"""
    print(f'task begin')
    ...  # 其他步骤
    print(f' begin big step')

    big_result = await big_step()

    print(f' end big step with {big_result}')
    ...  # 其他步骤

    print('task end')

    return 'one task end'


async def big_step():
    ...  # 其他小步骤
    print(f'  begin small step')

    small_result = await small_step()

    print(f'  end small step with {small_result}')
    ...  # 其他小步骤
    return small_result * 1000


async def small_step():
    sleep_time = random.random()
    t1 = time.time()
    await Awaitable(sleep_time)
    assert time.time() - t1 >= sleep_time, f'睡眠时间不足'
    return sleep_time


class Awaitable:
    def __init__(self, obj):
        self.value = obj

    def __await__(self):
        yield self
        return self.value


class Task:
    task_id_counter = itertools.count(1)

    def __init__(self, cor):
        self.cor = cor
        self._done = False
        self._result = None
        self._id = f'Task-{next(self.task_id_counter)}'

    def run(self):
        global loop
        print(f'----{self._id}------')
        if not self._done:
            try:
                x = self.cor.send(None)
            except StopIteration as e:
                self._result = e.value
                self._done = True
            else:
                assert isinstance(x, Awaitable)
                loop.call_later(x.value, self.run)  # 定时激活协程，根据yield的时间自动控制，即 await Awaitable(sleep_time)
        else:
            print(f'task is done')
        print('----------')


class EventLoop:
    def __init__(self):
        self._ready = collections.deque()  # 即将执行的任务（双向队列 先进先出）
        self._scheduled = []  # 定时任务（最小堆，时间最小的永远排在第一位）
        self._stopping = False

    def call_soon(self, callback, *args):
        self._ready.append((callback, args))

    def call_later(self, delta, callback, *args):
        t = time.time() + delta
        heapq.heappush(self._scheduled, (t, callback, args))

    def stop(self):
        self._stopping = True

    def run_forever(self):
        while True:
            self.run_once()
            if self._stopping:
                break

    def run_once(self):
        now = time.time()
        if self._scheduled:
            if self._scheduled[0][0] < now:
                _, cb, args = heapq.heappop(self._scheduled)
                self._ready.append((cb, args))  # 定时任务加到即将执行的任务队列

        num = len(self._ready)  # _ready这个列表会一直变动，所以取length（以某一时刻的列表长度为准）

        for i in range(num):
            cb, args = self._ready.popleft()  # 先进先出
            cb(*args)


if __name__ == '__main__':
    loop = EventLoop()
    # 异步操作，总共耗时1秒左右
    for i in range(10):
        t = Task(one_task())
        loop.call_soon(t.run)
    loop.call_later(1, loop.stop)  # 定时关闭事件循环
    loop.run_forever()
