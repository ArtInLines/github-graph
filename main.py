from neo4j import GraphDatabase
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

def req(endpoint, mapper = None):
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

class graph_node:
	name:  str   = ""
	edges: [int] = []
	def __init__(self, name):
		self.name  = name
		self.edges = []

def print_graph(g):
	print("Graph:")
	print("---------------")
	for node in g:
		print(node.name + ":")
		for edge in node.edges:
			print("   " + g[edge].name)

def get_forks(start_acc: str, degrees: int = 2, graph: [graph_node] = [], visited_accs: dict = {}, visited_repos: dict = {}):
	if start_acc in visited_accs:
		return graph
	res = len(graph)
	visited_accs[start_acc] = res
	acc_node = graph_node(start_acc)
	graph.append(acc_node)

	acc_repos = req(f"users/{start_acc}/repos", lambda x: x["full_name"])
	for repo in acc_repos:
		if repo in visited_repos:
			acc_node.edges.append(visited_repos[repo])
		else:
			visited_repos[repo] = len(graph)
			acc_node.edges.append(len(graph))
			repo_node = graph_node(repo)
			graph.append(repo_node)
			if degrees > 0:
				forks = req(f"repos/{repo}/forks", lambda x: x["full_name"])
				for fork in forks:
					if fork in visited_repos:
						repo_node.edges.append(visited_repos[fork])
					else:
						if degrees > 1:
							fork_acc = fork.split("/")[0]
							get_forks(fork_acc, degrees - 1, graph, visited_accs, visited_repos)
							repo_node.edges.append(visited_repos[fork])
						else:
							repo_node.edges.append(len(graph))
							visited_repos[fork] = len(graph)
							r = graph_node(fork)
							graph.append(r)
	return graph

if __name__ == "__main__":
	db = GraphDatabase.driver(os.getenv("DB_URI"), auth=(os.getenv("DB_USER"), os.getenv("DB_PASS")))
	db.verify_connectivity()
	graph = get_forks("Rex2002", 2)

	print("Syncing graph with neo4j...")
	db.execute_query("MATCH ()-[r]->() DELETE r")
	db.execute_query("MATCH (p) DELETE (p)")
	for node in graph:
		db.execute_query("MERGE (u:User {name: $name})", name=node.name.split("/")[0], database_="neo4j")
		if "/" in node.name:
			db.execute_query("MATCH (u:User {name: $username}) MERGE (u)-[o:OWNS]->(r:Repo {name: $reponame})", username=node.name.split("/")[0], reponame=node.name.split("/")[1], database_="neo4j")
	for node in graph:
		if "/" in node.name:
			for edge in node.edges:
				print(node.name + " -> " + graph[edge].name)
				db.execute_query("MATCH (u1:User {name: $user1}) MATCH (u1)-[:OWNS]->(r1:Repo {name: $repo1}) MATCH (u2:User {name: $user2}) MATCH (u2)-[:OWNS]->(r2:Repo {name: $repo2}) MERGE (r1)-[:FORKED_TO]->(r2)", user1=node.name.split("/")[0], repo1=node.name.split("/")[1], user2=graph[edge].name.split("/")[0], repo2=graph[edge].name.split("/")[1])

	print("Done :)")
	db.close()