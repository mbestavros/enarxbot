# SPDX-License-Identifier: Apache-2.0

import requests
import github
import os

class Suggestion:
    @classmethod
    def query(cls, github, repo, pr):
        reply = graphql(f"""
query {{
  repository(owner: "{repo.owner.login}", name: "{repo.name}") {{
    pullRequest(number: {pr.number}) {{
      suggestedReviewers {{
        isAuthor
        isCommenter
        reviewer {{
          login
        }}
      }}
    }}
  }}
}}
""")

        for x in reply["data"]["repository"]["pullRequest"]["suggestedReviewers"]:
            reviewer = github.get_user(x["reviewer"]["login"])
            yield cls(reviewer, x["isAuthor"], x["isCommenter"])

    def __init__(self, reviewer, author, commenter):
        self.reviewer = reviewer
        self.is_author = author
        self.is_commenter = commenter

def connect():
    token = os.environ.get('GITHUB_TOKEN', None)
    return github.Github(token)

def graphql(query):
    token = os.environ.get('GITHUB_TOKEN', None)
    json = { "query": query }
    headers = {}

    if token is not None:
        headers["Authorization"] = f"token {token}"

    reply = requests.post("https://api.github.com/graphql", json=json, headers=headers)
    if reply.status_code == 200:
        return reply.json()

    raise Exception(f"Query failed: {reply.status_code}! {query}")

def create_card(column, content_id, content_type):
    try:
        column.create_card(content_id=content_id, content_type=content_type)
    except github.GithubException as e:
        error = e.data["errors"][0]
        if error["resource"] != "ProjectCard" or error["code"] != "unprocessable":
            raise
        print("Card already in project.")