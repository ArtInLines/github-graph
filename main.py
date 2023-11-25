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

def get(url: str, **kwargs) -> requests.Response:
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
		timeout_len = int(reset) - time.time()
		print(f"\033[33m[INFO] Rate-Limited for {timeout_len}s\033[0m")
		time.sleep(timeout_len)
		return get(url, **kwargs)
	else:
		# No idea what happened
		print("\033[31m[ERROR] Received unknown status code: " + str(r.status_code) + "\033[0m")
		os._exit(1)

def get_json_list(endpoint, mapper = None):
	res = []
	payload = {
		"page": 1,
		"per_page": 100,
	}
	url = f"https://api.github.com/{endpoint}"
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

	try:
		user = get(f"https://api.github.com/users/{start_acc}", headers=headers).json()
		db.execute_query("""
			MATCH (u:User {name: $uname})
			SET u.avatar=$avatar
		""", uname=start_acc, avatar=user["avatar_url"])
		user = None
	except:
		print("\033[33m[WARNING] Couldn't get data for user '" + start_acc + "'\033[0m")
		return

	if degrees > 0:
		followers = get_json_list(f"users/{start_acc}/followers", lambda x: x["login"])
		for follower in followers:
			records, _, _ = db.execute_query("""
				MATCH (u1:User {name: $uname})
				MERGE (u2:User {name: $followername})
				ON CREATE SET u2.visited = 0
				MERGE (u1)<-[:FOLLOWS]-(u2)
				RETURN u2
			""", uname=start_acc, followername=follower)
			assert(len(records) == 1)
			u = records[0].value()
			if u['visited'] == 0:
				search(u['name'], db, degrees - 1)

		followees = get_json_list(f"users/{start_acc}/following", lambda x: x["login"])
		for followee in followees:
			records, _, _ = db.execute_query("""
				MATCH (u1:User {name: $uname})
				MERGE (u2:User {name: $followeename})
				ON CREATE SET u2.visited = 0
				MERGE (u1)-[:FOLLOWS]->(u2)
				RETURN u2
			""", uname=start_acc, followeename=followee)
			assert(len(records) == 1)
			u = records[0].value()
			if u['visited'] == 0:
				search(u['name'], db, degrees - 1)

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

				contributors = get_json_list(f"repos/{repo}/contributors", lambda x: x["login"])
				for contributor in contributors:
					records, _, _ = db.execute_query("""
						MATCH (r:Repo {name: $rname})
						MERGE (u:User {name: $uname})
						ON CREATE SET u.visited = 0
						CREATE (u)-[:CONTRIBUTED]->(r)
						RETURN u
					""", rname=repo, uname=contributor)
					assert(len(records) == 1)
					u = records[0].value()
					if u["visited"] == 0:
						search(u["name"], db, degrees - 1)

				stargazers = get_json_list(f"repos/{repo}/stargazers", lambda x: x["login"])
				for stargazer in stargazers:
					records, _, _ = db.execute_query("""
						MATCH (r:Repo {name: $rname})
						MERGE (u:User {name: $uname})
						ON CREATE SET u.visited = 0
						CREATE (u)-[:STARRED]->(r)
						RETURN u
					""", rname=repo, uname=stargazer)
					assert(len(records) == 1)
					u = records[0].value()
					if u["visited"] == 0:
						search(u["name"], db, degrees - 1)

if __name__ == "__main__":
	db = GraphDatabase.driver(os.getenv("DB_URI"), auth=(os.getenv("DB_USER"), os.getenv("DB_PASS")))
	db.verify_connectivity()

	clean_db(db)
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:User) REQUIRE x.name IS UNIQUE")
	db.execute_query("CREATE CONSTRAINT IF NOT EXISTS FOR (x:Repo) REQUIRE x.name IS UNIQUE")
	search("Rex2002", db, 1)

	print("Done :)")
	db.close()