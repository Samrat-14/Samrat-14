import hashlib

from pathlib import Path


def calculate_hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def load_cache(key: str) -> dict:
    filename = Path(f"cache/{calculate_hash(key)}.txt")
    if not filename.exists():
        return {}
    with filename.open("r", encoding="utf-8") as file:
        return {
            parts[0]: [int(x) for x in parts[1:]]
            for line in file
            if (parts := line.split())  # Splitting and filtering out empty lines at the same time
        }


def save_cache(key: str, cache: dict) -> None:
    filename = Path(f"cache/{calculate_hash(key)}.txt")
    with filename.open("w", encoding="utf-8") as file:
        file.writelines([
            f"{hash_key} {" ".join(map(str, metrics))}\n"
            for hash_key, metrics in cache.items()
        ])


def get_cached_repo(cache: dict, repo_name: str, commit_count: int) -> dict | None:
    repo_hash = hashlib.sha256(repo_name.encode("utf-8")).hexdigest()
    repo = cache.get(repo_hash) # [commit_count, commits, additions, deletions]

    if repo is None:
        return None
    
    if int(repo[0]) != commit_count:
        return None
    
    return {
        "commit_count": int(repo[0]),
        "commits": int(repo[1]),
        "additions": int(repo[2]),
        "deletions": int(repo[3]),
        "loc": int(repo[2]) - int(repo[3]),
    }


def update_repo_cache(cache: dict, repo_name: str, commit_count: int, stats: dict):
    repo_hash = calculate_hash(repo_name)
    cache[repo_hash] = [commit_count, stats["commits"], stats["additions"], stats["deletions"]]
