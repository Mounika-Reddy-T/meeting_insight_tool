from fastapi import FastAPI
from fastapi import HTTPException
from schemas import TextRequest, InsightResult
from ai_engine import generate_insights

app = FastAPI(title="Document Insight Service")


@app.get("/")
def status():
    return {"message": "Service running"}


@app.post("/analyze-document", response_model=InsightResult)
async def analyze_document(payload: TextRequest):
    try:
        result = await generate_insights(payload.text)
        return result
    except RuntimeError as exc:
        message = str(exc)
        status_code = 500 if "OPENROUTER_API_KEY is not configured" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from exc
