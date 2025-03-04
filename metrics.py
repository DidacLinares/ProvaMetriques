import os
import json
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
URL = f"https://api.github.com/repos/{REPO}/contributors"

response = requests.get(URL, headers=HEADERS)

if response.status_code != 200:
    print(f"Error en la trucada API a contributors: {response.status_code}")
    exit(1)

contributors = response.json()

commits_by_user = {}
total_commits = 0

for contributor in contributors:
    user = contributor["login"]
    commits = contributor["contributions"]

    if user != "github-actions[bot]":
        commits_by_user[user] = commits
        total_commits += commits

commits_data = {
    "Commits": commits_by_user
}
commits_data["Commits"]["Total"] = total_commits

json_file = "metrics.json"

if os.path.exists(json_file):
    with open(json_file, "r") as j:
        data = json.load(j)
else:
    data = {}

data["Commits"] = commits_data["Commits"]

with open(json_file, "w") as j:
    json.dump(data, j, indent=2)

