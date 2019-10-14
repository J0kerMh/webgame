import random
from application.__init__ import  mongo

###########
day = 600
package_limit = 10
weight = []
w = 1
for i in range(5):
    w*=3
    weight.append(w)
#############

def weighted_random(items):
    print("items is ",items)
    total = sum(w for _,w in items)
    n = random.uniform(0, total)#在饼图扔骰子
    for x, w in items:#遍历找出骰子所在的区间
        if n<w:
            break
        n -= w
    return x

def check_package_is_full(name):
    package = mongo.db.package.find_one({'name': name})
    item_list = package['item']
    item_num = len(package['item'])
    if item_num == package_limit:
        new_item_list = sorted(item_list, key = lambda k: k['quality'])
        for item in package['item']:
            if not item['on_sale']:
                package['item'].remove(item)
                return  package
    return {}
