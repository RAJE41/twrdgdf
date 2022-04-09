import requests, asyncio
from onesecmail import OneSecMail
from time import sleep
import random, string

async def reg():
	r = requests.Session()
	mail = OneSecMail.get_random_mailbox()
	address = mail.address
	passw = await randompass()

	token = r.post("https://web-api.hi-l.eu/api/auth/register/", json={"email": address, "password": passw}).json()["accessToken"]
	sleep(5)
	link = mail.get_messages()[0].body
	link = link[link.find('">')+2:link.find('</a>')]
	link = link.replace("hi-l.eu", "web-api.hi-l.eu/api/auth")
	r.get(link)
	ss = r.get("https://web-api.hi-l.eu/api/vpn/my/?limit=3&page=1", headers={"Authorization": f"Bearer {token}"}).json()["rows"][0]["accessUrl"]
	return address, passw, ss

async def randompass():
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(random.randint(10,20)))
