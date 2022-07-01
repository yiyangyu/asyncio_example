import collections
import functools
import itertools
import random
import sys
import time
from time import sleep
from functools import reduce


def one_task():
    """一个任务"""
    print(f'task begin')
    ...  # 其他步骤
    print(f' begin big step')

    big_result = big_step()

    print(f' end big step with {big_result}')
    ...  # 其他步骤

    print('task end')


def big_step():
    ...  # 其他小步骤
    print(f'  begin small step')

    small_result = small_step()

    print(f'  end small step with {small_result}')
    ...  # 其他小步骤
    return small_result * 1000


def small_step():
    print('   休息一下，马上回来')
    sleep(2)
    print('   努力工作中。。。')
    return 123  # 完成了


# 执行任务
# one_task()  # small_step 直接 sleep 2秒


from random import Random

random.random
