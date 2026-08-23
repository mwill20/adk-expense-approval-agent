import json
import os
from google.adk.cli.agent_test_runner import InMemoryRunner
import sys
from dotenv import load_dotenv

# Ensure the app directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from expense_agent.agent import root_agent

def main():
    with open("tests/eval/datasets/basic-dataset.json", "r") as f:
        dataset = json.load(f)
    
    traces = []
    
    for case in dataset:
        runner = InMemoryRunner(root_agent)
        events = []
        final_response = None
        
        payload_str = json.dumps(case["payload"])
        adk_events = runner.run(payload_str)
        
        has_interrupt = False
        for ev in adk_events:
            events.append({"author": "agent", "content": {"parts": [{"text": str(ev)}]}})
            if type(ev).__name__ == "RequestInput":
                has_interrupt = True
            elif hasattr(ev, "output") and ev.output:
                final_response = ev.output
        
        if has_interrupt:
            desc = case["payload"]["description"].lower()
            action = "approve"
            if "bypass" in desc or "ignore" in desc or "auto-approve" in desc or "disregard" in desc:
                action = "reject"
            
            from google.adk.types import Content, Part, FunctionResponse
            # To resume a RequestInput, we pass a FunctionResponse matching the interrupt_id
            resume_msg = Content(role="user", parts=[Part(function_response=FunctionResponse(name="manager_decision", response={"manager_decision": action}))])
            resumed_events = runner.run(resume_msg)
            
            for ev in resumed_events:
                events.append({"author": "agent", "content": {"parts": [{"text": str(ev)}]}})
                if hasattr(ev, "output") and ev.output:
                    final_response = ev.output
        
        trace = {
            "eval_case_id": case["id"],
            "prompt": {"role": "user", "parts": [{"text": payload_str}]},
            "responses": [
                {
                    "response": {"role": "model", "parts": [{"text": json.dumps(final_response, default=str)}]}
                }
            ],
            "agent_data": {
                "turns": [
                    {
                        "turn_index": 0,
                        "events": events
                    }
                ]
            }
        }
        traces.append(trace)
        
    os.makedirs("artifacts/traces", exist_ok=True)
    with open("artifacts/traces/generated_traces.json", "w") as f:
        json.dump({"eval_cases": traces}, f, indent=2)
    
    print("Successfully generated traces to artifacts/traces/generated_traces.json")

if __name__ == "__main__":
    main()
