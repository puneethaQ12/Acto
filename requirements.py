import sys, os, argparse
sys.path.insert(0, os.path.dirname(__file__))

from agent.github_fetcher import parse_github_url, fetch_relevant_files
from agent.static_extractor import run_static_extraction
from agent.schema_generator import enrich_endpoints_with_schemas
from agent.output_formatter import save_outputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="https://github.com/juice-shop/juice-shop")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  AKTO AI AGENT")
    print(f"  Repo: {args.repo}")
    print(f"{'='*50}\n")

    owner, repo = parse_github_url(args.repo)
    files = fetch_relevant_files(owner, repo)
    endpoints = run_static_extraction(files)
    enriched = enrich_endpoints_with_schemas(endpoints)
    save_outputs(enriched, args.output_dir)

if __name__ == "__main__":
    main()
```

Click **Commit new file** ✅

---

## File 3 → `agent/__init__.py`

Go to 👉 **https://github.com/puneethaQ12/Acto/new/main**

Filename:
```
agent/__init__.py
```
Leave content **completely empty**

Click **Commit new file** ✅

---

## File 4 → `agent/github_fetcher.py`

Go to 👉 **https://github.com/puneethaQ12/Acto/new/main**

Filename:
```
agent/github_fetcher.py