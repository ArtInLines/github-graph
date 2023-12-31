#!/usr/bin/env python
import signal
import threading
from neo4j import GraphDatabase, Driver
import requests
import json
from dotenv import dotenv_values
import os
import time
import math
from datetime import datetime
from sys import argv
env = dotenv_values("../.env")

PRINT_REQ_INFO = True
close_process = False

# API_TOKS and timeouts are two parallel arrays
API_TOKS = env["API_TOKEN"].split(",")
timeouts = []
for _ in range(len(API_TOKS)):
	timeouts.append(0)

def get_min_timeout_idx() -> int:
	min_timeout = timeouts[0]
	out         = 0
	cur_time = int(math.floor(time.time()))
	for i in range(1, len(timeouts)):
		if timeouts[i] < min_timeout:
			min_timeout = timeouts[i]
			out         = i
			if min_timeout < cur_time:
				break
	return out

def get_headers(api_tok_idx: int) -> dict:
	return {
		"Authorization": "Bearer " + API_TOKS[api_tok_idx],
	}

def is_rate_limited(res: requests.Response) -> bool:
	try:
		return res.status_code == 429 or (res.status_code == 403 and res.json()["message"].startswith("API rate limit exceeded"))
	except:
		return False

def get(url: str, to_print: bool = PRINT_REQ_INFO, **kwargs) -> requests.Response:
	api_tok_idx = get_min_timeout_idx()
	cur_time = int(math.floor(time.time()))
	if timeouts[api_tok_idx] > cur_time:
		time.sleep(timeouts[api_tok_idx] - cur_time)
	if to_print:
		print(f"[INFO] Making request with {api_tok_idx}. API-Token to {url}")
	kwargs["headers"] = get_headers(api_tok_idx)
	r = requests.get(url, **kwargs)

	if 200 <= r.status_code < 300:
		# Successfull request
		return r
	elif r.status_code == 404:
		raise Exception(r)
	elif is_rate_limited(r):
		# Rate Limited
		reset = r.headers["x-ratelimit-reset"]
		cur_time = int(math.floor(time.time()))
		timeouts[api_tok_idx] = int(reset)
		# Logging:
		until = datetime.fromtimestamp(int(reset)).strftime("%H:%M")
		print(f"\033[33m[INFO] Rate-Limited for {timeouts[api_tok_idx] - cur_time}s until {until} UTC\033[0m")
		return get(url, **kwargs)
	else:
		# No idea what happened
		print("\033[31m[ERROR] Received unknown status code: " + str(r.status_code) + " when requesting " + url + "\033[0m")
		raise Exception(r)

def get_json_list_threaded(url, payload, idx, arr, mapper):
	try:
		params = payload
		params["page"] = idx
		r = get(url, False, params=params)
		data = r.json()
		if mapper == None:
			for i in range(len(data)):
				arr[payload["per_page"] * idx + i] = data[i]
		else:
			for i in range(len(data)):
				arr[payload["per_page"] * idx + i] = mapper(data[i])
		return True
	except:
		return idx

def get_json_list(endpoint: str, mapper = None, max_amount: int = None):
	res = []
	payload = {
		"page": 1,
		"per_page": 100,
	}
	url = f"https://api.github.com/{endpoint}"
	if max_amount != None:
		req_amount = math.ceil(max_amount / payload["per_page"])
		if req_amount > 1:
			if PRINT_REQ_INFO:
				print("[INFO] Threading " + str(req_amount) + " GET calls to " + url)
			for i in range(max_amount):
				res.append(None)
			threads = []
			for i in range(req_amount):
				t = threading.Thread(target=get_json_list_threaded, args=(url, payload, i, res, mapper))
				t.start()
				threads.append(t)
			for t in threads:
				t.join()
		else:
			max_amount = None
	if max_amount == None:
		make_req = True
		while make_req:
			try:
				r = get(url, params=payload)
				data = r.json()
				if mapper != None:
					res += list(map(mapper, data))
				else:
					res += data
				# Check whether there is another page in the response
				# @Cleanup: This can probably be done simpler
				make_req = False
				payload["page"] += 1
				if "link" in r.headers:
					link  = r.headers["link"]
					links = link.split("; ")
					has_next = False
					for l in links:
						if l.startswith("rel=\"next\""):
							has_next = True
							break
					if has_next:
						make_req = True
			except:
				break
	return res

def clean_db(db: Driver):
	db.execute_query("MATCH (p) DETACH DELETE (p)")

def get_and_sync_list(db: Driver, endpoint: str, key: str, max: int, query: str, query_key: str = None, **query_args):
	data = get_json_list(endpoint, lambda x: x[key], max)
	for x in data:
		if query_key != None:
			query_args[query_key] = x
		records, _, _ = db.execute_query(query, **query_args)
		assert(len(records) == 1)

def get_forks(db: Driver, repo: str, forks_count: int):
	forks = get_json_list(f"repos/{repo}/forks", lambda x: x["full_name"], forks_count)
	for fork in forks:
		records, _, _ = db.execute_query("""
			MERGE (r:Repo {name: $rname})
			ON CREATE SET r.visited=0
			RETURN r
		""", rname=fork)
		assert(len(records) == 1)
		r = records[0].value()
		records, _, _ = db.execute_query("""
			MATCH (r1:Repo {name: $r1name})
			MATCH (r2:Repo {name: $r2name})
			MERGE (r1)-[rel:FORKED_TO]->(r2)
		""", r1name=repo, r2name=fork)
		if r['visited'] == 0:
			db.execute_query("""
				MATCH (r:Repo {name: $rname})
				MATCH (u:User {name: $uname})
				MERGE (u)-[:OWNS]->(r)
			""", rname=fork, uname=fork.split("/")[0])

def get_contributors(db: Driver, repo: str):
	contributors = get_json_list(f"repos/{repo}/contributors", lambda x: [x["login"], int(x["contributions"])])
	total_contributions = 0
	for x in contributors:
		total_contributions += x[1]
	for contributor in contributors:
		db.execute_query("""
			MATCH (r:Repo {name: $rname})
			MERGE (u:User {name: $uname})
				ON CREATE SET u.visited = 0
			MERGE (u)-[x:CONTRIBUTED]->(r)
			SET x.weight=$w, x.contributions=$c
		""", uname=contributor[0], rname=repo, w=1-(contributor[1]/total_contributions), c=contributor[1])

def get_langs(db: Driver, repo: str):
	langs = get_json_list(f"repos/{repo}/languages")
	total_loc = 0
	if isinstance(langs, list):
		ls = {}
		for l in langs:
			ls[l] = 1
		langs = ls
	if len(langs) == 0:
		langs['Other'] = 1
	for _, loc in langs.items():
		total_loc += loc
	for lang, loc in langs.items():
		db.execute_query("""
			MATCH (r:Repo {name: $rname})
			MERGE (l:Lang {name: $lname})
			MERGE (r)-[x:WRITTEN_IN]->(l)
			SET x.abs=$lines, x.rel=$perc
		""", lname=lang, rname=repo, lines=loc, perc=loc/total_loc)

def search(start_acc: str, db: Driver):
	print("[INFO] Starting search for user " + start_acc)
	records, _, _ = db.execute_query("""
		MERGE (u:User {name: $uname})
		ON CREATE SET u.visited=0
		ON MATCH SET u.visited=u.visited + toInteger(u.visited > 0)
		RETURN u
	""", uname=start_acc)
	assert(len(records) == 1)
	if records[0].value()['visited'] > 1:
		print("[INFO] User " + start_acc + " was already visited before")
		return # This account was visited before already

	followers_count = None
	following_count = None
	repos_count     = None
	try:
		user = get(f"https://api.github.com/users/{start_acc}").json()
		db.execute_query("""
			MATCH (u:User {name: $uname})
			SET u.avatar=$avatar
		""", uname=start_acc, avatar=user["avatar_url"])
		followers_count = user["followers"]
		following_count = user["following"]
		repos_count     = user["public_repos"]
	except:
		db.execute_query("""MATCH (u:User {name: $uname}) SET u.visited = -1""", uname=start_acc)
		print("\033[33m[WARNING] Couldn't get data for user '" + start_acc + "'\033[0m")
		return

	visited_repos = {}
	threads       = []

	t = threading.Thread(target=get_and_sync_list, args=(db, f"users/{start_acc}/followers", "login", followers_count, """
		MATCH (u1:User {name: $uname})
		MERGE (u2:User {name: $followername})
		ON CREATE SET u2.visited = 0
		MERGE (u1)<-[:FOLLOWS]-(u2)
		RETURN u2
	""", "followername"), kwargs={"uname": start_acc})
	t.start()
	threads.append(t)

	t = threading.Thread(target=get_and_sync_list, args=(db, f"users/{start_acc}/following", "login", following_count, """
		MATCH (u1:User {name: $uname})
		MERGE (u2:User {name: $followeename})
		ON CREATE SET u2.visited = 0
		MERGE (u1)-[:FOLLOWS]->(u2)
		RETURN u2
	""", "followeename"), kwargs={"uname": start_acc})
	t.start()
	threads.append(t)

	repos = get_json_list(f"users/{start_acc}/repos", lambda x: x["full_name"], repos_count)
	for repo in repos:
		try:
			r = get(f"https://api.github.com/repos/{repo}").json()
			stargazers_count = int(r["stargazers_count"])
			forks_count = int(r["forks_count"])

			records, _, _ = db.execute_query("""
				MATCH (u:User {name: $uname})
				MERGE (r:Repo {name: $rname})
				ON CREATE SET r.visited=0
				ON MATCH SET r.visited=r.visited + toInteger(r.visited > 0)
				MERGE (u)-[:OWNS]->(r)
				RETURN r
			""", uname=start_acc, rname=repo)
			assert(len(records) == 1)
			r = records[0].value()
			# @Cleanup: I'm not sure if it should be possible for a repo to have been visited before if we didn't visit its user yet
			# I do know, that I counted visits in previously buggy versions though, so as to correct those, I added the 'or True' for now
			if r['visited'] <= 1 or True:
				t = threading.Thread(target=get_forks, args=(db, repo, forks_count))
				t.start()
				threads.append(t)

				t = threading.Thread(target=get_contributors, args=(db, repo))
				t.start()
				threads.append(t)

				t = threading.Thread(target=get_langs, args=(db, repo))
				t.start()
				threads.append(t)

				t = threading.Thread(target=get_and_sync_list, args=(db, f"repos/{repo}/stargazers", "login", stargazers_count, """
					MATCH (r:Repo {name: $rname})
					MERGE (u:User {name: $uname})
					ON CREATE SET u.visited = 0
					MERGE (u)-[:STARRED]->(r)
					RETURN u
				""", "uname"), kwargs={"rname": repo})
				t.start()
				threads.append(t)
				visited_repos[len(threads) - 1] = repo
		except:
			db.execute_query("""MATCH (u:Repo {name: $rname}) SET u.visited = -1""", rname=repo)
			print("\033[031m[ERROR] Failed to get data for " + repo + "\033[0m")

	for i in range(len(threads)):
		threads[i].join()
		if i in visited_repos:
			db.execute_query("""MATCH (r:Repo {name: $rname}) SET r.visited=1""", rname=visited_repos[i])
	records, _, _ = db.execute_query("""
		MATCH (u:User {name: $uname})
		SET u.visited = 1
	""", uname=start_acc)

def signal_handler(sig, frame):
	if not close_process:
		print('\033[033m[INFO] Ending process soon\033[0m')
		globals()["close_process"] = True
	else:
		print('\033[033m[INFO] Process was violently closed - bye\033[0m')
		os._exit(0)

def main():
	if len(argv) > 2:
		print("\033[31mInvalid Amount of arguments\033[0m")
		print("Usage:")
		print(f"> python3 {argv[0]} [<Account to start Search from> | -fix]")
		print("")
		print("Examples:")
		print(f"> python3 {argv[0]}")
		print(f"> python3 {argv[0]} ArtInLines")
		print(f"> python3 {argv[0]} -fix")
		os._exit(1)

	db = GraphDatabase.driver(env["DB_URI"], auth=(env["DB_USER"], env["DB_PASS"]))
	db.verify_connectivity()
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:User) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:Repo) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:Lang) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE INDEX IF NOT EXISTS FOR (x:User) ON (x.name)")
	db.execute_query("CREATE INDEX IF NOT EXISTS FOR (x:Repo) ON (x.name)")
	db.execute_query("CREATE INDEX IF NOT EXISTS FOR (x:Lang) ON (x.name)")

	acc = None
	if len(argv) >= 2:
		acc = argv[1]
	else:
		records, _, _ = db.execute_query("""MATCH (u:User {visited: 0}) RETURN u.name LIMIT 1""")
		if len(records) == 0:
			print("\033[31mNo starting account can be determined, please provide one\033[0m")
			os._exit(0)
		acc = records[0].value()
	while not close_process:
		search(acc, db)
		records, _, _ = db.execute_query("""MATCH (u:User {visited: 0}) RETURN u.name LIMIT 1""")
		if len(records) == 0:
			break
		acc = records[0].value()

	db.close()

def fix_db():
	db = GraphDatabase.driver(env["DB_URI"], auth=(env["DB_USER"], env["DB_PASS"]))
	db.verify_connectivity()
	print("Connected to database")

	records, _, _ = db.execute_query("""
		MATCH (r:Repo)
		WHERE NOT EXISTS ((r)-[:WRITTEN_IN]->(:Lang))
		RETURN r.name
	""")
	print(f"Found {len(records)} repos to fix")
	for rec in records:
		if close_process:
			break
		rname = rec.value()
		get_langs(db, rname)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	if len(argv) == 2 and argv[1] == '-fix':
		fix_db()
	else:
		main()