from dataclasses import dataclass, field


@dataclass
class GitHubStats:
    age: str = ""
    followers: int = 0
    contributions: int = 0
    pull_requests: int = 0

    repositories: int = 0
    stars: int = 0
    forks: int = 0
    archived_repositories: int = 0

    commits: int = 0
    additions: int = 0
    deletions: int = 0
    loc: int = 0

    languages: dict[str, int] = field(default_factory=dict)