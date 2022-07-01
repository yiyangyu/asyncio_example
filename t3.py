import time
from time import sleep


def one_task():
    """一个任务"""
    print(f'task begin')
    ...  # 其他步骤
    print(f' begin big step')

    # big_result = big_step() # 普通函数
    big_cor = big_step()  # 协程，因为有了yield，同时承担了不断激活子协程的任务
    while True:
        try:
            x = big_cor.send(None)
        except StopIteration as e:
            big_result = e.value
            break
        else:
            func, arg = x  # x = 最下游协程yield出来的 (sleep, 2) 这个tuple
            func(arg)  # 将下游的sleep 转化成了 上游的sleep

    print(f' end big step with {big_result}')
    ...  # 其他步骤

    print('task end')


def big_step():
    ...  # 其他小步骤
    print(f'  begin small step')

    # small_result = small_step() # 普通函数
    small_cor = small_step()  # 协程，因为有了yield

    while True:
        try:
            x = small_cor.send(None)
        except StopIteration as e:
            small_result = e.value
            break
        else:
            yield x  # 把子协程的yield值抛给上游去处理

    print(f'  end small step with {small_result}')
    ...  # 其他小步骤
    return small_result * 1000


def small_step():
    print('   休息一下，马上回来')
    t1 = time.time()
    yield sleep, 2
    assert time.time() - t1 >= 2, '睡眠时间不足2秒'
    print('   努力工作中。。。')
    return 123  # 完成了


# 执行任务
one_task()

"""
1. 协程自己不能消除阻塞
2. 协程具有传染性，普通函数变成协程函数后，对应的上游的调用方式也要改变
3. 协程通过 yield 把下游的阻塞转换成了上游的阻塞
4. 阻塞需要其他解决方案
"""
