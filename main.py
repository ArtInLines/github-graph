import requests
import json
import dotenv
import os
import time
dotenv.load_dotenv()

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

def get_forks(start_acc: str, visited_accs: dict, visited_repos: dict, graph: [graph_node], degress: int = 2):
	if start_acc in visited_accs:
		return
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
							get_forks(fork_acc, visited_accs, visited_repos, graph, degrees - 1)
							repo_node.edges.append(visited_repos[fork])
						else:
							repo_node.edges.append(len(graph))
							visited_repos[fork] = len(graph)
							r = graph_node(fork)
							graph.append(r)

start_acc     = "Rex2002"
visited_accs  = {}
visited_repos = {}
graph         = []
degrees       = 2
get_forks(start_acc, visited_accs, visited_repos, graph, degrees)
print_graph(graph)
# print("")
# print("Visited:")
# print("----------------")
# for x in visited_accs:
# 	print(x + ": " + str(visited_accs[x]))
# for x in visited_repos:
# 	print(x + ": " + str(visited_repos[x]))