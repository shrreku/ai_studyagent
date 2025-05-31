import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload_routes, study_plan_routes, chat_routes

app = FastAPI(title="Study Agent API")

# Get allowed origins from environment or use defaults
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://studyagent-v2.vercel.app",  # Vercel deployment (update with your actual domain)
]

# Add custom domain if specified in environment
if os.environ.get("FRONTEND_URL"):
    allowed_origins.append(os.environ.get("FRONTEND_URL"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(upload_routes.router)
app.include_router(study_plan_routes.router, prefix="/plan", tags=["Study Plan"])
app.include_router(chat_routes.router, tags=["Chat"]) # No prefix needed as routes already have /chat prefix

@app.get("/")
def read_root():
    return {"message": "Welcome to the Study Agent API"}