import random
from app_sql import *
###########
day = 600
package_limit = 10
tool_limit = 1
decoration_limit = 1
weight = []
w = 1
for i in range(5):
    w*=3
    weight.append(w)
#############

def weighted_random(items):
    # print("items is ",items)
    total = sum(w for _,w in items)
    n = random.uniform(0, total)#在饼图扔骰子
    for x, w in items:#遍历找出骰子所在的区间
        if n<w:
            break
        n -= w
    return x

def check_package_is_full(name):
    if Item.query.filter_by(owner = name, is_used=False).all():
       return False
    else:
        if Item.query.filter_by(owner = name, is_used=False).count() >= package_limit:
            removed_item = Item.query.filter_by(owner = name, on_sale = False, is_used = False).order_by(Item.quality).first()
            if removed_item:
                db.session.delete(removed_item)
                db.session.commit()
                return False
            else:
                return True
        return False