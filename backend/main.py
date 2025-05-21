from fastapi import FastAPI
from routers import upload_routes, study_plan_routes, chat_routes

app = FastAPI()

app.include_router(upload_routes.router)
app.include_router(study_plan_routes.router, prefix="/plan", tags=["Study Plan"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"]) # Added chat router

@app.get("/")
def read_root():
    return {"message": "Welcome to the Study Agent API"}