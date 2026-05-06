import requests

# Test root endpoint
r = requests.get('http://127.0.0.1:5001/')
title = r.text[r.text.find('<title>')+7:r.text.find('</title>')]
print(f'Root title: {title}')

# Test /v2 endpoint
r2 = requests.get('http://127.0.0.1:5001/v2')
print(f'/v2 status: {r2.status_code}')
if r2.status_code == 200:
    title2 = r2.text[r2.text.find('<title>')+7:r2.text.find('</title>')]
    print(f'/v2 title: {title2}')
