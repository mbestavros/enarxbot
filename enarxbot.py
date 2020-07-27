# SPDX-License-Identifier: Apache-2.0

import requests
import github
import os

ORGANIZATION_LABELS = {
    'amd sev': {
        'name': 'amd sev',
        'description': 'Issues related to AMD SEV',
        'color': '000000'
    },
    'bug': {
        'name': 'bug',
        'description': "Something isn't working",
        'color': 'd73a4a'
    },
    'conference': {
        'name': 'conference',
        'description': 'Opportunities to talk about Enarx',
        'color': 'f98918'
    },    
    'debt': {
        'name': 'debt',
        'description': 'Issues to deal with later',
        'color': '0c0c75'
    },    
    'documentation': {
        'name': 'documentation',
        'description': 'Improvements or additions to documentation',
        'color': 'efef15'
    },    
    'duplicate': {
        'name': 'duplicate',
        'description': 'This issue or pull request already exists',
        'color': 'cfd3d7'
    },    
    'enhancement': {
        'name': 'enhancement',
        'description': 'New feature or request',
        'color': 'a2eeef'
    },    
    'expertise needed': {
        'name': 'expertise needed',
        'description': 'This needs special attention from an area specialist.',
        'color': 'f9928e'
    },    
    'good first issue': {
        'name': 'good first issue',
        'description': 'Good for newcomers',
        'color': 'a8f475'
    },    
    'help wanted': {
        'name': 'help wanted',
        'description': 'Extra attention is needed',
        'color': '008672'
    },    
    'host-components': {
        'name': 'host-components',
        'description': 'Components that live on the host, but not in Keeps',
        'color': 'f22933'
    },    
    'ibm pef': {
        'name': 'ibm pef',
        'description': 'Issues related to IBM PEF',
        'color': '0043ce'
    },    
    'infrastructure': {
        'name': 'infrastructure',
        'description': 'Improvements or additions to project infrastructure',
        'color': 'ffdda8'
    },    
    'intel sgx': {
        'name': 'intel sgx',
        'description': 'Issues related to Intel SGX',
        'color': '0071c5'
    },    
    'invalid': {
        'name': 'invalid',
        'description': "This doesn't seem right", 'color': 'e4e669'
    },    
    'mentorship': {
        'name': 'mentorship',
        'description': 'A request for mentorship on the project.',
        'color': '0e8a16'
    },    
    'meta': {
        'name': 'meta',
        'description': 'Larger project tasks and goals',
        'color': '149e7b'
    },    
    'question': {
        'name': 'question',
        'description': 'Further information is requested',
        'color': 'd876e3'
    },    
    'research': {
        'name': 'research',
        'description': '',
        'color': 'ed8661'
    },    
    'security': {
        'name': 'security',
        'description': 'Issues that have security implications',
        'color': 'ff0000'
    },    
    'syscall': {
        'name': 'syscall',
        'description': 'syscall-related issues and PRs',
        'color': 'a51f3c'
    },    
    'wasm': {
        'name': 'wasm',
        'description': 'Issues related to WebAssembly',
        'color': '654EF0'
    },    
    'wontfix': {
        'name': 'wontfix',
        'description': 'This will not be worked on',
        'color': 'ffffff'
    }
}

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
