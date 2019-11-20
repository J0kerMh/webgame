import requests
a=requests.Session()
# response = requests.post('http://127.0.0.1:5000/signup',data={'name':'yhma','F_pwd':'test','S_pwd':'test'})
re= a.post('http://127.0.0.1:5000/login',data={'name':'yhma','pwd':'test'})
response = a.get('http://127.0.0.1:5000/user')
#
# response = a.post('http://127.0.0.1:5000/user/opts',data={'opts':'work','args':'test'})
# response = a.post('http://127.0.0.1:5000/user/opts',data={'opts':'treasure_hunt','args':'test'})
# response = a.post('http://127.0.0.1:5000/user/opts',data={'opts':'adorn_tool','args':'general ron cloudsensei'})
# response = a.post('http://127.0.0.1:5000/user/opts',data={'opts':'adorn_tool','args':'general ron cloudsensei'})
# response = requests.post()
print(response.text)
# import silly
# import random
# from app_sql.utils import *
# def random_item():
#     item_name = silly.name()
#     if (random.randint(0, 9) % 2):
#         category = 'tool'
#     else:
#         category = 'decoration'
#     luck = 6
#     from app_sql.utils import weight
#     weight = [j + (2 ** luck) for j in weight]
#     quality = weighted_random(tuple(zip(reversed(range(1, 6)), weight)))
#     # quality = weighted_random(weighted_item)
#     print( item_name, category, quality, False, False)
#
# random_item()