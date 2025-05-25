from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload_routes, study_plan_routes, chat_routes

app = FastAPI(title="Study Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
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