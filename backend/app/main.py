from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.core.database import init_db

# Initialize database
init_db()

app = FastAPI(
    title="Skin Disease Detection API",
    description="A backend combining EfficientNet CV and Gemini LLM for skin disease analysis with persistent chat history",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the endpoints from routes.py to the main application
app.include_router(router)
app.include_router(auth_router)


@app.get("/")
def health_check():
    """Simple check to ensure the server is running."""
    return {"status": "healthy", "message": "API is up and running!"}
