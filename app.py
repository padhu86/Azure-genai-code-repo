from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests

app = FastAPI()

# Template setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# APIM details
APIM_ENDPOINT = "https://apim-dev-southindia-01.azure-api.net/dev/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

# Chat endpoint
@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    user_query = body.get("message")

    if not user_query:
        return {"response": "Please enter a question"}

    # 🔥 Get key at runtime
    APIM_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")

    if not APIM_KEY:
        return {
            "response": "Configuration error: APIM key missing"
        }

    try:
        response = requests.post(
            APIM_ENDPOINT + f"&subscription-key={APIM_KEY}",   # ✅ Query param
            headers={
                "Content-Type": "application/json",
                "api-key": APIM_KEY   # ✅ Header
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_query}
                ]
            },
            timeout=30
        )

        data = response.json()

        # ✅ Success case
        if "choices" in data:
            return {
                "response": data["choices"][0]["message"]["content"]
            }

        # ❌ Error case
        return {
            "response": f"APIM Error ({response.status_code}): {data}"
        }

    except Exception as e:
        return {
            "response": f"Exception occurred: {str(e)}"
        }

# Test APIM endpoint
@app.get("/test-apim")
async def test_apim():
    APIM_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")

    return {
        "key_present": APIM_KEY is not None,
        "key_preview": APIM_KEY[:5] if APIM_KEY else None
    }
