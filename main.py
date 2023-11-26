import threading
from neo4j import GraphDatabase, Driver
import requests
import json
import dotenv
import os
import time
import math
from datetime import datetime
dotenv.load_dotenv()

timeout_len = 0
print_req_info = True
headers = {
	"Authorization": "Bearer " + os.getenv("API_TOKEN"),
}

def get(url: str, **kwargs) -> requests.Response:
	timeout_len = globals()["timeout_len"]
	if timeout_len > 0:
		time.sleep(timeout_len)
		globals()["timeout_len"] = 0
	if print_req_info:
		print("[INFO] Making request to " + url)
	r = requests.get(url, **kwargs)

	if 200 <= r.status_code < 300:
		# Successfull request
		return r
	elif r.status_code == 404:
		raise Exception(r)
	elif r.status_code in (403, 429):
		# Rate Limited
		reset = r.headers["x-ratelimit-reset"]
		cur_time = int(math.floor(time.time()))
		timeout_len = int(reset) - cur_time
		if (timeout_len > 3600):
			timeout_len = 3600
		globals()["timeout_len"] = timeout_len
		until = datetime.fromtimestamp(int(reset)).strftime("%H:%M")
		print(f"\033[33m[INFO] Rate-Limited for {timeout_len}s until {until} UTC\033[0m")
		time.sleep(timeout_len)
		globals()["timeout_len"] = 0
		return get(url, **kwargs)
	else:
		# No idea what happened
		print("\033[31m[ERROR] Received unknown status code: " + str(r.status_code) + "\033[0m")
		os._exit(1)

def get_json_list_threaded(url, payload, idx, arr, mapper):
	try:
		params = payload
		params["page"] = idx
		r = get(url, params=params, headers=headers)
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
			if print_req_info:
				print("[INFO] Threading " + str(req_amount) + " GET calls at once")
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
				r = get(url, params=payload, headers=headers)
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

def get_and_sync_list(res: [int], idx: int, db: Driver, degrees: int, endpoint: str, key: str, max: int, query: str, query_key: str = None, **query_args):
	threads = []
	data = get_json_list(endpoint, lambda x: x[key], max)
	for x in data:
		records = []
		if query_key != None:
			query_args[query_key] = x
		records, _, _ = db.execute_query(query, **query_args)
		assert(len(records) == 1)
		u = records[0].value()
		if u['visited'] == 0:
			t = threading.Thread(target=search, args=(u['name'], db, degrees - 1))
			t.start()
			threads.append(t)
	res[idx] = threads

def search(start_acc: str, db: Driver, degrees: int = 2):
	records, _, _ = db.execute_query("""
		MERGE (u:User {name: $uname})
		ON CREATE SET u.visited=1
		ON MATCH SET u.visited=u.visited+1
		RETURN u
	""", uname=start_acc)
	assert(len(records) == 1)
	if records[0].value()['visited'] > 1:
		return # This account was visited before already

	followers_count = None
	following_count = None
	try:
		user = get(f"https://api.github.com/users/{start_acc}", headers=headers).json()
		db.execute_query("""
			MATCH (u:User {name: $uname})
			SET u.avatar=$avatar
		""", uname=start_acc, avatar=user["avatar_url"])
		followers_count = user["followers"]
		following_count = user["following"]
		user = None
	except:
		print("\033[33m[WARNING] Couldn't get data for user '" + start_acc + "'\033[0m")
		return

	meta_threads = []
	threads      = []
	if degrees > 0:
		threads.append(None)
		t = threading.Thread(target=get_and_sync_list, args=(threads, len(threads) - 1, db, degrees, f"users/{start_acc}/followers", "login", followers_count, """
			MATCH (u1:User {name: $uname})
			MERGE (u2:User {name: $followername})
			ON CREATE SET u2.visited = 0
			MERGE (u1)<-[:FOLLOWS]-(u2)
			RETURN u2
		""", "followername"), kwargs={"uname": start_acc})
		t.start()
		meta_threads.append(t)

		# threads.append(None)
		# t = threading.Thread(target=get_and_sync_list, args=(threads, len(threads) - 1, db, degrees, f"users/{start_acc}/following", "login", following_count, """
		# 	MATCH (u1:User {name: $uname})
		# 	MERGE (u2:User {name: $followeename})
		# 	ON CREATE SET u2.visited = 0
		# 	MERGE (u1)-[:FOLLOWS]->(u2)
		# 	RETURN u2
		# """, "followeename"), kwargs={"uname": start_acc})
		# t.start()
		# meta_threads.append(t)

		repos = get_json_list(f"users/{start_acc}/repos", lambda x: x["full_name"])
		for repo in repos:
			records, _, _ = db.execute_query("""
				MATCH (u:User {name: $uname})
				MERGE (r:Repo {name: $rname})
				ON CREATE SET r.visited=1
				ON MATCH SET r.visited=r.visited+1
				MERGE (u)-[:OWNS]->(r)
				RETURN r
			""", uname=start_acc, rname=repo)
			assert(len(records) == 1)
			r = records[0].value()
			if r['visited'] <= 1:
				forks = get_json_list(f"repos/{repo}/forks", lambda x: x["full_name"])
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
						CREATE (r1)-[rel:FORKED_TO]->(r2)
					""", r1name=repo, r2name=fork)
					if r['visited'] == 0:
						db.execute_query("""
							MATCH (r:Repo {name: $rname})
							MATCH (u:User {name: $uname})
							CREATE (u)-[:OWNS]->(r)
						""", rname=fork, uname=fork.split("/")[0])
						search(fork.split("/")[0], db, degrees-1)

				threads.append(None)
				t = threading.Thread(target=get_and_sync_list, args=(threads, len(threads) - 1, db, degrees, f"repos/{repo}/contributors", "login", None, """
					MATCH (r:Repo {name: $rname})
					MERGE (u:User {name: $uname})
					ON CREATE SET u.visited = 0
					CREATE (u)-[:CONTRIBUTED]->(r)
					RETURN u
				""", "uname"), kwargs={"rname": repo})
				t.start()
				meta_threads.append(t)

				# threads.append(None)
				# t = threading.Thread(target=get_and_sync_list, args=(threads, len(threads) - 1, db, degrees, f"repos/{repo}/stargazers", "login", None, """
				# 	MATCH (r:Repo {name: $rname})
				# 	MERGE (u:User {name: $uname})
				# 	ON CREATE SET u.visited = 0
				# 	CREATE (u)-[:STARRED]->(r)
				# 	RETURN u
				# """, "uname"), kwargs={"rname": repo})
				# t.start()
				# meta_threads.append(t)
	for mt in meta_threads:
		mt.join()
	for ts in threads:
		for t in ts:
			t.join()

if __name__ == "__main__":
	start = time.time()
	db = GraphDatabase.driver(os.getenv("DB_URI"), auth=(os.getenv("DB_USER"), os.getenv("DB_PASS")))
	db.verify_connectivity()
	clean_db(db)
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:User) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:Repo) REQUIRE x.name IS UNIQUE")

	search_start = time.time()
	search("Rex2002", db, 2)
	search_end   = time.time()

	expected_nodes_len = 39
	expected_edges_len = 88
	expected_visited_users_len = 29
	nodes, _, _ = db.execute_query("MATCH (p) RETURN p")
	edges, _, _ = db.execute_query("MATCH ()-[r]->() RETURN r")
	visited_users, _, _ = db.execute_query("MATCH (p:User) WHERE p.avatar IS NOT NULL RETURN p")
	if len(nodes) == expected_nodes_len:
		print("\033[32m#nodes = " + str(len(nodes)) + "\033[0m")
	else:
		print("\033[31m#nodes = " + str(len(nodes)) + "\033[0m")
	if len(edges) == expected_edges_len:
		print("\033[32m#edges = " + str(len(edges)) + "\033[0m")
	else:
		print("\033[31m#edges = " + str(len(edges)) + "\033[0m")
	if len(visited_users) == expected_visited_users_len:
		print("\033[32m#visited_users = " + str(len(visited_users)) + "\033[0m")
	else:
		print("\033[31m#visited_users = " + str(len(visited_users)) + "\033[0m")

	db.close()
	end = time.time()
	print("Total Time:    " + str(round(end - start, 3)) + "s")
	print("Searcing Time: " + str(round(search_end - search_start, 3)) + "s")