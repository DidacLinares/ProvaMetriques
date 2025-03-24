import os
import json
import requests
import datetime


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
today = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}
BASE_URL = "https://api.github.com/repos"

contributors_url = f"{BASE_URL}/{REPO}/contributors"
response_contributors = requests.get(contributors_url, headers=HEADERS)

if response_contributors.status_code != 200:
    print(f"Error en la trucada API a contributors: {response_contributors.status_code}")
    exit(1)

contributors = response_contributors.json()
commits_by_user = {}
total_commits = 0

for contributor in contributors:
    user = contributor["login"]
    commits = contributor["contributions"]
    if user != "github-actions[bot]":
        commits_by_user[user] = commits
        total_commits += commits

data = {"Commits": commits_by_user}
data["Commits"]["Total"] = total_commits

issues_url = f"{BASE_URL}/{REPO}/issues?state=all"
response_issues = requests.get(issues_url, headers=HEADERS)

if response_issues.status_code == 200:
    issues = response_issues.json()
    issues_by_user = {}
    total_issues = 0
    non_assigned_issues = 0
    
    for issue in issues:
        if 'pull_request' in issue:
            continue
        if 'assignees' in issue and issue['assignees']:
            total_issues += 1
            assignees = issue['assignees']
            for assignee in assignees:
                assignee_login = assignee['login']
                issues_by_user[assignee_login] = issues_by_user.get(assignee_login, 0) + 1
        else:
            non_assigned_issues += 1
            total_issues += 1
    
    issues_data = issues_by_user
    issues_data["Non-Assigned"] = non_assigned_issues
    issues_data["Total"] = total_issues
    data["Issues"] = issues_data
else:
    print(f"Error obtenint les issues: {response_issues.status_code}")

json_file = "daily_metrics.json"
if os.path.exists(json_file):
    with open(json_file, "r") as j:
        data_json = json.load(j)
else:
    data_json = {}

data_json[today] = data

with open(json_file, "w") as j:
    json.dump(data_json, j, indent=4)
