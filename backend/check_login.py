import urllib.request, urllib.parse, json
url = 'http://127.0.0.1:8000/api/auth/login'
data = urllib.parse.urlencode({'username': 'hod@example.com', 'password': 'hod@123'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
try:
    resp = urllib.request.urlopen(req, timeout=5)
    print('STATUS', resp.status)
    body = resp.read().decode()
    print(body)
except Exception as e:
    print('ERROR', type(e).__name__, e)
