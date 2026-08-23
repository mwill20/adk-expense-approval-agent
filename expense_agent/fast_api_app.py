import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from google.adk.cli.fast_api import get_fast_api_app

logging.basicConfig(level=logging.INFO)

# Create the FastAPI app mounting the ADK workflow
app = get_fast_api_app(
    agents_dir=".",
    web=False,
    a2a=False,
    trigger_sources=['pubsub'],
    otel_to_cloud=False,
)

class NormalizePubSubMiddleware(BaseHTTPMiddleware):
    """
    Middleware to normalize the fully-qualified subscription path 
    to a short name to keep session records readable.
    """
    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/trigger/pubsub") and request.method == "POST":
            body = await request.body()
            if body:
                try:
                    payload = json.loads(body)
                    if "subscription" in payload:
                        sub = payload["subscription"]
                        if "/" in sub:
                            # e.g., projects/my-project/subscriptions/expense-topic-sub -> expense-topic-sub
                            payload["subscription"] = sub.split("/")[-1]
                            
                        # Replace the request body stream for downstream processing
                        async def receive():
                            return {"type": "http.request", "body": json.dumps(payload).encode("utf-8")}
                        request._receive = receive
                except Exception as e:
                    logging.error(f"Error normalizing pubsub subscription: {e}")
        return await call_next(request)

# Add the normalization middleware
app.add_middleware(NormalizePubSubMiddleware)
