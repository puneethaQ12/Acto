def generate_schema_static_fallback(endpoint: dict) -> dict:
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "/")
    path_params = endpoint.get("path_params", [])
    body_fields = endpoint.get("body_fields", [])
    query_fields = endpoint.get("query_fields", [])
    requires_auth = endpoint.get("requires_auth", False)

    path_params_schema = {
        p: {"type": "string", "description": f"Path parameter: {p}"}
        for p in path_params
    }
    query_schema = {f: {"type": "string"} for f in query_fields}
    body_schema = {}
    if body_fields and method in ("POST", "PUT", "PATCH"):
        body_schema = {
            "type": "object",
            "properties": {f: {"type": "string"} for f in body_fields}
        }

    tags = []
    p = path.lower()
    if any(x in p for x in ["user", "login", "register", "password"]):
        tags.append("Users & Auth")
    if any(x in p for x in ["product", "search"]):
        tags.append("Products")
    if any(x in p for x in ["basket", "cart"]):
        tags.append("Basket")
    if "order" in p:
        tags.append("Orders")
    if "feedback" in p:
        tags.append("Feedback")
    if any(x in p for x in ["card", "wallet", "payment"]):
        tags.append("Payment")
    if "address" in p:
        tags.append("Address")
    if any(x in p for x in ["challenge", "continue-code"]):
        tags.append("Challenges")
    if any(x in p for x in ["admin", "config", "version"]):
        tags.append("Admin")
    if not tags:
        tags.append("General")

    return {
        "summary": f"{method} {path}",
        "description": f"Extracted from {endpoint.get('source_file', 'unknown')}",
        "requires_auth": requires_auth,
        "tags": tags,
        "request_schema": {
            "path_params": path_params_schema,
            "query_params": query_schema,
            "body": body_schema
        },
        "response_schema": {
            "200": {"description": "Success"},
            "400": {"description": "Bad Request"},
            "401": {"description": "Unauthorized"} if requires_auth else {},
            "500": {"description": "Internal Server Error"}
        },
        "security_notes": "Requires JWT Bearer token" if requires_auth else "Public endpoint - no auth required"
    }

def enrich_endpoints_with_schemas(endpoints: list, api_key=None, use_llm=False) -> list:
    enriched = []
    total = len(endpoints)
    for i, ep in enumerate(endpoints):
        print(f"  [{i+1}/{total}] {ep['method']} {ep['path']}")
        schema = generate_schema_static_fallback(ep)
        enriched.append({**ep, "schema": schema})
    return enriched