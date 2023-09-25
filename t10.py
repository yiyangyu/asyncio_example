import collections
import heapq
import itertools
import random
import threading
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
    global loop
    fut = Future()
    # 指派一个目标来执行 set_result, 即IO阻塞一段时间后给future对象赋值
    fake_io_read(fut)
    result = await fut
    return result


def fake_io_read(future):
    def read():
        sleep(random.random())  # 模拟io阻塞
        future.set_result(random.randint(1, 100))

    threading.Thread(target=read).start()


class Future:
    def __init__(self):
        global loop
        self._loop = loop
        self._result = None
        self._done = False
        self._callbacks = []

    def set_result(self, result):
        if self._done:
            raise RuntimeError('future already done.')
        self._result = result
        self._done = True

        for cb in self._callbacks:  # set_result后，由事件循环执行所有回调函数
            self._loop.call_soon(cb)

    def result(self):
        if not self._done:
            raise RuntimeError('future is not done.')
        return self._result

    def is_done(self):
        return self._done

    def add_done_callback(self, callback):
        self._callbacks.append(callback)

    def __await__(self):
        yield self
        return self.result()


class Task(Future):
    task_id_counter = itertools.count(1)

    def __init__(self, cor):
        super().__init__()
        self.cor = cor
        self._id = f'Task-{next(self.task_id_counter)}'
        self._loop.call_soon(self.run)  # 创建实例就直接添加到事件循环中
        self._start_time = time.time()

    def run(self):
        print(f'----{self._id}------')
        if not self._done:
            try:
                x = self.cor.send(None)
            except StopIteration as e:
                self.set_result(e.value)
                global total_block_time
                total_block_time += time.time() - self._start_time  # 协程结束计算每个协程的耗时
            else:
                assert isinstance(x, Future)  # yield 的是一个 Future对象
                # 我什么时候能恢复执行?
                x.add_done_callback(self.run)  # 回调函数列表中添加了这个task的run函数，用于激活协程
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


def util_all_done(_tasks):
    global loop
    _tasks = [_ for _ in _tasks if not _.is_done()]

    if _tasks:
        loop.call_soon(util_all_done, _tasks)  # 由事件循环不停执行，直到所有task结束
    else:
        loop.stop()


if __name__ == '__main__':
    loop = EventLoop()
    total_block_time = 0
    task_count = 5000
    start_time = time.time()
    tasks = [Task(one_task()) for i in range(task_count)]
    loop.call_soon(util_all_done, tasks)  # 代替手动执行loop.stop，检测tasks全部结束后自动stop
    # loop.call_later(0.1, util_all_done, tasks)  # 代替手动执行loop.stop，检测tasks全部结束后自动stop
    # loop.call_later(1, loop.stop)
    loop.run_forever()  # 设置了所有的立刻执行任务and定时任务之后再执行run_forever
    done_task_count = sum(t.is_done() for t in tasks)
    assert task_count == done_task_count, f'任务总数 {task_count} 结束任务 {done_task_count}'
    print(total_block_time, time.time() - start_time)

# 总结
"""
yield 是主动协程，最先出栈
yield from 是跟随 yield 的被动协程，紧跟着 yield 出栈
yield from 简化了被动协程的代码，不用写大量的 while

yield from 作用仅仅是作为管道（透传），连接了调用方(send) 与最底层的协程函数(yield)

调用 send，激活协程, 主动入栈
yield from 仅仅作为管道依次传递中间的被动协程，直到遇到 yield, 子协程主动出栈，yield from 也跟着出栈，最底层yield的值传递给最上层send表达式，
等到再次send激活协程后，主动协程代码从yield处继续运行，被动协程从yield from处继续运行，循环往复，直到遇到return(StopIteration), 
协程函数(不管是主动的yield还是被动的yield from)的return值会传给yield from（或者说 await）


asycio 新语法
await = yield from
__await__ = __iter__
"""
