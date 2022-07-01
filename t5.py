import time
from time import sleep


def one_task():
    """一个任务"""
    print(f'task begin')
    ...  # 其他步骤
    print(f' begin big step')

    big_result = yield from big_step()

    print(f' end big step with {big_result}')
    ...  # 其他步骤

    print('task end')
    return 'one task'


def big_step():
    ...  # 其他小步骤
    print(f'  begin small step')

    small_result = yield from small_step()

    print(f'  end small step with {small_result}')
    ...  # 其他小步骤
    return small_result * 1000


def small_step():
    print('   休息一下，马上回来')
    t1 = time.time()
    # yield sleep, 2
    yield from YieldFromAble((sleep, 2))  # 引入一个 子协程YieldFromAble
    assert time.time() - t1 > 2, '睡眠时间不足2秒'
    print('   努力工作中。。。')
    return 123  # 完成了


class YieldFromAble:
    def __init__(self, obj):
        self.value = obj

    def __iter__(self):
        yield self


class Task:
    def __init__(self, cor):
        self.cor = cor

    def run(self):
        print('----------')
        while True:
            try:
                x = self.cor.send(None)
            except StopIteration as e:
                result = e.value
                # print(f'result {result}')
                break
            else:
                assert isinstance(x, YieldFromAble)
                func, arg = x.value
                func(arg)
        print('----------')


# 执行任务
t = Task(one_task())
t.run()

"""
yield 是主动协程，最先出栈
yield from 是跟随 yield 的被动协程，紧跟着 yield 出栈
yield from 简化了被动协程的代码，不用写大量的 while

调用 send 主动入栈，激活协程
yield from 仅仅作为管道依次传递中间的被动协程，直到遇到 yield, 子协程主动出栈，yield from 也跟着出栈，yield的值传递给send表达式，
等到再次send激活协程后，代码从yield处继续运行，循环往复，直到遇到return(StopIteration), 会把return的value传给yield from(await)表达式
"""
