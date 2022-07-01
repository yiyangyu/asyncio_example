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
    print('   休息一下，马上回来')
    t1 = time.time()
    await Awaitable((sleep, 2))
    assert time.time() - t1 > 2, '睡眠时间不足2秒'
    print('   努力工作中。。。')
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


# 执行任务

t = Task(one_task())
t.run()

# 假设协程需要等待2秒的时间，在这期间主动yield出栈，主动让出代码执行权给其他任务

for i in range(10):
    print('doing something')
    time.sleep(0.2)

t.run()
