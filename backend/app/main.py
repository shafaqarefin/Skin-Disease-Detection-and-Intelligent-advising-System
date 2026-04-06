from fastapi import FastAPI
from app.api.routes import router
app = FastAPI(
    title="Skin Disease Detection API",
    description="A  backend combining EfficientNet CV and Gemini LLM for skin disease analysis",
    version="1.0.0"
)

# Connect the endpoints from routes.py to the main application
app.include_router(router)


@app.get("/")
def health_check():
    """Simple check to ensure the server is running."""
    return {"status": "healthy", "message": "API is up and running!"}
