# Security Policy

## Reporting

Report privately via GitHub's **Report a vulnerability** button under this
repository's *Security* tab. Please do not open a public issue for a security
finding. Personal project; no SLA, no bounty.

## Posture

### What is deliberate

- **The approval boundary is deterministic.** `route_expense` compares
  `amount` against `EXPENSE_THRESHOLD` in plain Python. No model output decides
  whether an expense requires human review, so a prompt-injected or simply wrong
  model response cannot route a large expense into auto-approval.
- **Human-in-the-loop above the threshold.** `review_agent` suspends on a
  `RequestInput` interrupt and cannot self-resolve; a human must supply
  `manager_decision`.
- **Typed input.** Workflow input is a Pydantic `ExpenseReport`, so malformed
  payloads fail at the boundary rather than downstream.
- **No secrets committed.** `.env`, `*.tfvars`, Terraform state, and the ADK
  session DB are gitignored. `.env.example` carries placeholders only.

### Known gaps

- **The resume input is not validated.** `review_agent` lowercases and strips
  `manager_decision` but accepts any string; anything that is not `approve` is
  recorded verbatim as `final_decision` rather than being rejected against an
  allowlist.
- **No authorization on the approver.** The workflow does not verify that the
  party answering the interrupt is entitled to approve that expense, or that
  they are not the submitter. Self-approval is not prevented here.
- **No audit trail of the decision.** The final event carries the decision but
  the workflow does not independently log actor, timestamp, and payload for
  forensic reconstruction.
- **Free-text fields reach the model.** `description` and `category` come from
  the submitter. The eval set includes an `attacker@company.com` case, but
  adversarial coverage is a handful of examples, not a systematic red-team.

Treat this as a demonstration of the control pattern, not as a deployable
approval system.
