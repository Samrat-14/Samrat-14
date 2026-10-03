import requests


GITHUB_API_URL = "https://api.github.com/graphql"

PROFILE_QUERY = """
query {
    viewer {
        followers {
            totalCount
        }
        repositories {
            totalCount
        }
        contributionsCollection {
            contributionCalendar {
                totalContributions
            }
        }
    }
}
"""

PULL_REQUEST_COUNT_QUERY = """
query($query: String!) {
    search(
        query: $query
        type: ISSUE
        first: 1
    ) {
        issueCount
    }
}
"""

REPOSITORIES_QUERY = """
query($cursor: String) {
    viewer {
        repositories(
            first: 100
            after: $cursor
            ownerAffiliations: OWNER
            orderBy: {
                field: UPDATED_AT
                direction: DESC
            }
        ) {
            nodes {
                name
                nameWithOwner
                url
                stargazerCount
                forkCount
                isFork
                isArchived
                createdAt
                updatedAt
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history {
                                totalCount
                            }
                        }
                    }
                }
                languages(first: 20) {
                    edges {
                        size
                        node {
                            name
                        }
                    }
                }
            }

            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
}
"""

COMMITS_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
    repository(owner: $owner, name: $name) {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100, after: $cursor) {
                        nodes {
                            oid
                            author {
                                user {
                                    login
                                }
                            }
                            additions
                            deletions
                        }

                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
    }
}
"""


class GitHubClient:
    def __init__(self, token: str):
        self.token = token

    def _query(self, query: str, variables: dict | None = None):
        response = requests.post(
            GITHUB_API_URL,
            json={"query": query, "variables": variables or {}},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise RuntimeError(data["errors"])
        return data["data"]

    def get_profile(self):
        data = self._query(PROFILE_QUERY)
        return data["viewer"]

    def get_pull_request_count(self, username: str) -> int:
        data = self._query(
            PULL_REQUEST_COUNT_QUERY,
            variables={"query": f"is:pr author:{username}"},
        )
        return data["search"]["issueCount"]

    def get_repositories(self):
        repositories = []
        cursor = None
        while True:
            data = self._query(REPOSITORIES_QUERY, variables={"cursor": cursor})
            connection = data["viewer"]["repositories"]
            repositories.extend(connection["nodes"])
            if not connection["pageInfo"]["hasNextPage"]:
                break
            cursor = connection["pageInfo"]["endCursor"]
        return repositories

    def get_commits(self, owner: str, name: str):
        commits = []
        cursor = None
        while True:
            data = self._query(
                COMMITS_QUERY,
                variables={"owner": owner, "name": name, "cursor": cursor},
            )
            repository = data["repository"]
            if repository is None:
                break
            branch = repository["defaultBranchRef"]
            if branch is None:
                break
            history = branch["target"]["history"]
            commits.extend(history["nodes"])
            if not history["pageInfo"]["hasNextPage"]:
                break
            cursor = history["pageInfo"]["endCursor"]
        return commits
