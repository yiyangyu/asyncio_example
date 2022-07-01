from time import sleep


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

    # small_result = small_step()
    small_cor = small_step()  # 由于函数内部存在yield, 变成生成器了

    # 一直激活生成器 small_cor 并且得到 small_cor 的return值
    while True:
        try:
            x = small_cor.send(None)
            # print('send...')
        except StopIteration as e:
            small_result = e.value
            break
        else:
            ...
            # print(f'yield {x}')  # 接收到生成器yield的值

    print(f'  end small step with {small_result}')
    ...  # 其他小步骤
    return small_result * 1000


def small_step():
    print('   休息一下，马上回来')
    yield 123
    yield sleep(2)  # 阻塞了整个主线程2秒，sleep函数返回None
    print('   努力工作中。。。')
    return 123  # 完成了


# 执行任务
one_task()  # small_step sleep 2秒, 但是加入了 yield
