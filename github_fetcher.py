import requests
import base64
import time
from typing import Optional

GITHUB_API = "https://api.github.com"

def get_repo_tree(owner: str, repo: str, branch: str = "master") -> list:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
    resp.raise_for_status()
    return resp.json().get("tree", [])

def get_file_content(owner: str, repo: str, path: str) -> Optional[str]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers={"Accept": "application/vnd.github+json"})
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return data.get("content")

def parse_github_url(url: str) -> tuple:
    parts = url.rstrip("/").split("/")
    return parts[-2], parts[-1]

def fetch_relevant_files(owner: str, repo: str) -> dict:
    print(f"[*] Fetching file tree for {owner}/{repo}...")
    tree = get_repo_tree(owner, repo)

    relevant_patterns = [
        lambda p: p.startswith("routes/") and p.endswith(".ts"),
        lambda p: p in ("server.ts", "app.ts"),
        lambda p: p == "swagger.yml",
        lambda p: p.startswith("models/") and p.endswith(".ts"),
        lambda p: "Services/" in p and p.endswith(".ts"),
        lambda p: p.startswith("lib/") and p.endswith(".ts"),
    ]

    files_to_fetch = [
        item["path"] for item in tree
        if item["type"] == "blob" and any(pat(item["path"]) for pat in relevant_patterns)
    ]

    print(f"[*] Found {len(files_to_fetch)} relevant files. Fetching contents...")

    contents = {}
    for i, path in enumerate(files_to_fetch):
        content = get_file_content(owner, repo, path)
        if content:
            contents[path] = content
        if i > 0 and i % 10 == 0:
            time.sleep(1)

    print(f"[*] Successfully fetched {len(contents)} files.")
    return contents