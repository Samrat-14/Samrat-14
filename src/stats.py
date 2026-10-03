from datetime import datetime
from dateutil import relativedelta

from cache import get_cached_repo, update_repo_cache
from models import GitHubStats


def calculate_age(birthday):
    """
    Returns the length of time since I was born
    e.g. "XX years, XX months, XX days"
    """
    diff = relativedelta.relativedelta(datetime.today(), birthday)
    return "{} {}, {} {}, {} {}{}".format(
        diff.years, "year" + format_plural(diff.years), 
        diff.months, "month" + format_plural(diff.months), 
        diff.days, "day" + format_plural(diff.days),
        " 🎂" if (diff.months == 0 and diff.days == 0) else "")


def format_plural(unit):
    """
    Returns a properly formatted number of years, months, or days with the correct pluralization.
    """
    return "s" if unit != 1 else ""


def calculate_commit_stats(commits: list[dict], username: str):
    commit_count = 0
    additions = 0
    deletions = 0
    for commit in commits:
        author = commit.get("author")
        if author is None:
            continue
        if author.get("user") is None:
            continue
        if author["user"]["login"] != username:
            continue
        commit_count += 1
        additions += commit["additions"]
        deletions += commit["deletions"]
    return {
        "commits": commit_count,
        "additions": additions,
        "deletions": deletions,
        "loc": additions - deletions,
    }


def get_repository_stats(client, cache: dict, repo: dict, username: str):
    owner, name = repo["nameWithOwner"].split("/", 1)
    commit_count = repo["defaultBranchRef"]["target"]["history"]["totalCount"]
    cached_stats = get_cached_repo(cache, repo["nameWithOwner"], commit_count)
    if cached_stats is not None:
        return cached_stats
    commits = client.get_commits(owner, name)
    stats = calculate_commit_stats(commits, username)
    update_repo_cache(cache, repo["nameWithOwner"], commit_count, stats)
    return {
        "commit_count": commit_count,
        **stats,
    }


def calculate_global_stats(client, repositories: list[dict], cache: dict, username: str):
    total_commits = 0
    total_additions = 0
    total_deletions = 0
    for repo in repositories:
        stats = get_repository_stats(client, cache, repo, username)
        total_commits += stats["commits"]
        total_additions += stats["additions"]
        total_deletions += stats["deletions"]
    return {
        "commits": total_commits,
        "additions": total_additions,
        "deletions": total_deletions,
        "loc": total_additions - total_deletions,
    }


def calculate_repository_stats(repositories: list[dict]):
    total_repositories = 0
    total_stars = 0
    total_forks = 0
    archived_repositories = 0
    for repo in repositories:
        total_repositories += 1
        total_stars += repo["stargazerCount"]
        total_forks += repo["forkCount"]
        if repo["isArchived"]:
            archived_repositories += 1
    return {
        "repositories": total_repositories,
        "stars": total_stars,
        "forks": total_forks,
        "archived_repositories": archived_repositories,
    }


def calculate_profile_stats(profile: dict):
    return {
        "followers": profile["followers"]["totalCount"],
        "contributions": profile["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    }


def calculate_language_stats(repositories: list[dict]):
    languages = {}
    for repo in repositories:
        for edge in repo["languages"]["edges"]:
            language = edge["node"]["name"]
            size = edge["size"]
            languages[language] = (languages.get(language, 0) + size)
    return languages


def calculate_all_stats(client, profile: dict, repositories: list[dict], cache: dict, username: str) -> GitHubStats:
    my_age = calculate_age(datetime(2002, 5, 9))
    profile_stats = calculate_profile_stats(profile)
    repository_stats = calculate_repository_stats(repositories)
    commit_stats = calculate_global_stats(client, repositories, cache, username)
    pull_requests = client.get_pull_request_count(username)
    language_stats = calculate_language_stats(repositories)

    return GitHubStats(
        age=my_age,
        followers=profile_stats["followers"],
        repositories=repository_stats["repositories"],
        stars=repository_stats["stars"],
        forks=repository_stats["forks"],
        archived_repositories=repository_stats["archived_repositories"],
        commits=commit_stats["commits"],
        additions=commit_stats["additions"],
        deletions=commit_stats["deletions"],
        loc=commit_stats["loc"],
        contributions=profile_stats["contributions"],
        pull_requests=pull_requests,
        languages=language_stats,
    )