install:
	uv sync

playground:
	uv run agents-cli playground

serve:
	uv run uvicorn expense_agent.fast_api_app:app --host 0.0.0.0 --port 8080

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	uv run --env-file .env agents-cli eval grade --traces artifacts/traces/generated_traces.json --config tests/eval/eval_config.yaml --project mock-project
