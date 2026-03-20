import re
import yaml

ROUTE_PATTERN = re.compile(
    r'(?:router|app)\s*\.\s*(get|post|put|patch|delete|all|use)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
    re.IGNORECASE
)
PARAM_PATTERN = re.compile(r':(\w+)')
BODY_FIELD_PATTERN = re.compile(r'req\.body\.(\w+)')
QUERY_FIELD_PATTERN = re.compile(r'req\.query\.(\w+)')
AUTH_PATTERNS = [
    re.compile(r'security\.isAuthorized'),
    re.compile(r'passport\.authenticate'),
    re.compile(r'isAuthenticated'),
    re.compile(r'jwt\.verify'),
    re.compile(r'security\.denyAll'),
]

def extract_routes_from_file(path: str, content: str) -> list:
    routes = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        matches = ROUTE_PATTERN.findall(line)
        for method, route_path in matches:
            context = '\n'.join(lines[i:i+30])
            path_params = PARAM_PATTERN.findall(route_path)
            body_fields = list(set(BODY_FIELD_PATTERN.findall(context)))
            query_fields = list(set(QUERY_FIELD_PATTERN.findall(context)))
            requires_auth = any(pat.search(context) for pat in AUTH_PATTERNS)
            routes.append({
                "method": method.upper(),
                "path": route_path,
                "source_file": path,
                "path_params": path_params,
                "body_fields": body_fields,
                "query_fields": query_fields,
                "requires_auth": requires_auth,
                "raw_context": context[:500]
            })
    return routes

def extract_swagger_endpoints(swagger_content: str) -> list:
    try:
        spec = yaml.safe_load(swagger_content)
        endpoints = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "source_file": "swagger.yml",
                        "summary": details.get("summary", ""),
                        "from_swagger": True
                    })
        return endpoints
    except Exception as e:
        print(f"[!] Could not parse swagger.yml: {e}")
        return []

def normalize_path(path: str) -> str:
    return re.sub(r':(\w+)', r'{\1}', path)

def deduplicate_endpoints(endpoints: list) -> list:
    seen = {}
    for ep in endpoints:
        key = (ep["method"], normalize_path(ep.get("path", "")))
        if key not in seen:
            seen[key] = ep
        elif ep.get("from_swagger"):
            seen[key] = ep
    return list(seen.values())

def run_static_extraction(files: dict) -> list:
    all_endpoints = []
    for path, content in files.items():
        if path == "swagger.yml":
            eps = extract_swagger_endpoints(content)
            print(f"  [swagger] Found {len(eps)} endpoints")
            all_endpoints.extend(eps)
        elif path.startswith("routes/") or path in ("server.ts", "app.ts"):
            eps = extract_routes_from_file(path, content)
            if eps:
                print(f"  [routes] {path}: {len(eps)} endpoints")
            all_endpoints.extend(eps)
    deduped = deduplicate_endpoints(all_endpoints)
    print(f"\n[*] Total unique endpoints extracted: {len(deduped)}")
    return deduped