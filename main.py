import requests
from pprint import pprint
import socket
import re
from bs4 import BeautifulSoup
def spacer(left,right,length):
	l = abs(length - len(left))
	space = " " * l
	return left + space + right
HOST = "localhost"
PORT = 43
try:
	srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	srv.bind((HOST, PORT))
	srv.listen()
	print("Fediwhois is running")
	while True:
		client, addr = srv.accept()
		with client:
			raw_id = client.recv(1024).strip().decode()
			print(f"whois request was sent to {raw_id}")
			if (re.match('^@?.+@.+',raw_id)):
				user_id=raw_id
				if (user_id.startswith("@")):
					user_id = user_id[1:]
				id = user_id.split("@")[0]
				server = user_id.split("@")[1]
				error = False
				try:
					webfinger = requests.get(f'https://{server}/.well-known/webfinger?resource=acct:{user_id}')
					webfinger_json = webfinger.json()
					user_link = list(filter(lambda x: x["rel"] == "self", webfinger_json["links"]))[0]
					headers = {
						'Accept': 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
					}
					user = requests.get(user_link['href'], headers=headers)
					user_json = user.json()
					soup = BeautifulSoup(user_json["summary"])
					prettyHTML = "\n" + soup.prettify()
					user_detail = {
						'id': user_json["id"],
						'preferred_username': user_json["preferredUsername"],
						'server': server,
						'name': user_json["name"],
						'summaly': prettyHTML,
						'url': user_json["url"],
						'icon': user_json["icon"]["url"],
					}
					pprint(user_detail)
				except:
					error = True
				if (error):
					res = bytes(f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% This is the Fediwhois server.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#User Detail
================================
Error: This user is not Activitypub Actor: {user_id}
===============================
#Server Detail
===============================
TODO
""","utf-8")
					client.sendall(res)
				else:
					res = bytes(f"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% This is the Fediwhois server.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#User Detail
================================
{spacer("preferred_full_username: ",f"@{user_id}",25)}
{spacer("id: ",user_detail["id"],25)}
{spacer("server: ",user_detail["server"],25)}
{spacer("name: ",user_detail["name"],25)}
{spacer("summaly: ",user_detail["summaly"],25)}
{spacer("url: ",user_detail["url"],25)}
{spacer("icon: ",user_detail["icon"],25)}
===============================
#Server Detail
===============================
TODO
""","utf-8")
					client.sendall(res)
except KeyboardInterrupt:
	srv.close()
