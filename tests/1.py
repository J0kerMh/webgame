import requests

# response = requests.post('http://127.0.0.1:5000/signup',data={'name':'test','F_pwd':'test','S_pwd':'test'})
response = requests.post('http://127.0.0.1:5000/login',data={'name':'test','pwd':'test'})
print(response.text)