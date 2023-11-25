from neo4j import GraphDatabase, Driver
import requests
import json
import dotenv
import os
import time
dotenv.load_dotenv()

print_req_info = True
headers = {
	"Authorization": "Bearer " + os.getenv("API_TOKEN"),
}

def req_list(endpoint, mapper = None):
	res = []
	payload = {
		"page": 1,
		"per_page": 100,
	}
	url = f"https://api.github.com/{endpoint}"
	make_req = True
	while make_req:
		r = requests.get(url, params=payload, headers=headers)
		if print_req_info:
			print("[INFO] Making request to " + url)
		if 200 <= r.status_code < 300:
			# Successfull request
			forks = r.json()
			if mapper != None:
				res += list(map(mapper, forks))
			else:
				res += forks
		elif r.status_code in (403, 429):
			# Rate Limited
			reset = r.headers["x-ratelimit-reset"]
			timeout_len = int(reset) - time.time()
			print(f"\033[33m[INFO] Rate-Limited for {timeout_len}s\033[0m")
			time.sleep(timeout_len)
		else:
			# No idea what happened
			print("\033[31m[ERROR] Received unknown status code: " + str(r.status_code) + "\033[0m")
			os._exit(1)
		# Check whether there is another page in the response
		# @Cleanup: This can probably be done simpler
		payload["page"] += 1
		make_req = False
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
	return res

def clean_db(db: Driver):
	db.execute_query("MATCH (p) DETACH DELETE (p)")


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
	user = requests.get(f"https://api.github.com/users/{start_acc}", headers=headers)
	assert(200 <= user.status_code < 300)
	db.execute_query("""
		MATCH (u:User {name: $uname})
		SET u.avatar=$avatar
	""", uname=start_acc, avatar=user.json()["avatar_url"])
	user = None

	repos = req_list(f"users/{start_acc}/repos", lambda x: x["full_name"])
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
			forks = req_list(f"repos/{repo}/forks", lambda x: x["full_name"])
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

if __name__ == "__main__":
	db = GraphDatabase.driver(os.getenv("DB_URI"), auth=(os.getenv("DB_USER"), os.getenv("DB_PASS")))
	db.verify_connectivity()

	clean_db(db)
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:User) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:Repo) REQUIRE x.name IS UNIQUE")
	search("Rex2002", db)

	print("Done :)")
	db.close()