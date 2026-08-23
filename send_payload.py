import subprocess
import json

payload = json.dumps({
    "amount": 150.0, 
    "submitter": "alice@company.com", 
    "category": "software", 
    "description": "IDE License", 
    "date": "2026-06-06"
})

print(f"Sending payload: {payload}")
subprocess.run(["uv", "run", "agents-cli", "run", "--app-name", "expense_agent", payload])
