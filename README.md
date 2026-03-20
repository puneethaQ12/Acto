# Akto AI Agent

AI agent that extracts API endpoints from GitHub repos and generates OpenAPI 3.0 schemas.

## How to Run
pip install requests pyyaml
python main.py --repo https://github.com/juice-shop/juice-shop

## Results
- 58 endpoints extracted from OWASP Juice Shop
- 38 require JWT authentication  
- 20 public endpoints
- Output: openapi_spec.yaml, api_summary_report.json
