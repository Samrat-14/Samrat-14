import os

from github import GitHubClient
from stats import calculate_all_stats
from cache import load_cache, save_cache
from svg import render_stats_svgs


def main():
    token = os.environ["ACCESS_TOKEN"]
    username = "Samrat-14"

    client = GitHubClient(token)

    print("Fetching profile...")
    profile = client.get_profile()

    print("Fetching repositories...")
    repositories = client.get_repositories()

    print(f"Found {len(repositories)} repositories.")

    cache = load_cache(username)
    print("Calculating statistics...")
    stats = calculate_all_stats(client, profile, repositories, cache, username)
    save_cache(username, cache)

    print("Rendering SVGs...")
    render_stats_svgs(stats, "stats", "stats")

    print("Done!")


if __name__ == "__main__":
    main()