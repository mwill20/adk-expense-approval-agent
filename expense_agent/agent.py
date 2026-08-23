import re
from typing import Literal

from pydantic import BaseModel
from google.adk.workflow import Workflow, node
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context

from .config import EXPENSE_THRESHOLD, MODEL_NAME

class ExpenseReport(BaseModel):
    amount: float
    submitter: str
    category: str
    description: str
    date: str

@node
def route_expense(node_input: ExpenseReport | dict):
    if isinstance(node_input, dict):
        node_input = ExpenseReport(**node_input)
        
    if node_input.amount < EXPENSE_THRESHOLD:
        return Event(output=node_input, route="auto_approve")
    else:
        return Event(output=node_input, route="review_agent")

@node
def auto_approve(node_input: ExpenseReport):
    # Deterministic auto-approval for < $100
    return Event(
        output={
            "status": "approved", 
            "reason": "auto-approved (under threshold)", 
            "report": node_input.model_dump()
        }
    )

@node(rerun_on_resume=True)
def review_agent(ctx: Context, node_input: ExpenseReport | dict):
    if not ctx.resume_inputs:
        if isinstance(node_input, dict):
            node_input = ExpenseReport(**node_input)
        
        msg = f"Expense of ${node_input.amount} from {node_input.submitter} for '{node_input.description}' requires review. Please respond with 'approve' or 'reject'."
        
        yield RequestInput(interrupt_id="manager_decision", message=msg)
        return
        
    # The workflow resumed! Extract the manager's decision
    decision = ctx.resume_inputs.get("manager_decision", "").strip().lower()
    
    # Return the final approved or rejected status
    yield Event(output={"final_decision": decision, "input_received": node_input})


root_agent = Workflow(
    name="expense_agent_workflow",
    edges=[
        ('START', route_expense),
        (route_expense, {"auto_approve": auto_approve, "review_agent": review_agent}),
    ],
    input_schema=ExpenseReport
)