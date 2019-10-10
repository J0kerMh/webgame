import random

def weighted_random(items):
    print("items is ",items)
    total = sum(w for _,w in items)
    n = random.uniform(0, total)#在饼图扔骰子
    for x, w in items:#遍历找出骰子所在的区间
        if n<w:
            break
        n -= w
    return x

# weight = []
# w = 1
# for i in range(5):
#     w*=3
#     weight.append(w)
#
# quality = range(1,6)
# test = tuple(zip(reversed(quality), weight))
#
# print(test)
# print(weighted_random(test))
# for i in range(5):
#     weight = [j+(2**i) for j in weight]
#     # weight+=(3**(i-1))
#     all = sum(w for w in weight)
#     print([j/all for j in weight])
import time
import random
import silly
print(silly.name())

# print(random.randint(0,9)%2)
