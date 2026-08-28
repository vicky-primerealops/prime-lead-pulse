import requests

url = 'https://prime-lead-pulse.vercel.app/api/emails'

# I don't have a valid user token, but I can see if it returns 400 or 500 when missing fields!
res = requests.post(url, json={})
print(res.status_code, res.text)
