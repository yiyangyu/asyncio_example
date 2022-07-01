import collections
import heapq
import random
import time
from time import sleep


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
    t1 = time.time()
    await Awaitable((sleep, 2))
    assert time.time() - t1 >= 2, f'睡眠时间不足2秒, 只有{time.time() - t1}'
    return 123  # 完成了


class Awaitable:
    def __init__(self, obj):
        self.value = obj

    def __await__(self):
        yield self
        return self.value


class Task:
    def __init__(self, cor):
        self.cor = cor
        self._done = False
        self._result = None

    def run(self):
        print('----------')
        if not self._done:
            try:
                x = self.cor.send(None)
            except StopIteration as e:
                self._result = e.value
                self._done = True
            else:
                assert isinstance(x, Awaitable)
                # func, arg = x.value
                # func(arg)
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
    t = Task(one_task())
    start = time.time()

    loop.call_soon(t.run)
    loop.call_later(2.01, t.run)  # 2秒后再次执行t.run（以此模拟IO耗时2秒的效果），激活协程
    loop.call_later(2.01, loop.stop)  # 定时关闭事件循环
    loop.run_forever()

    print(f'time cost {time.time() - start}')
