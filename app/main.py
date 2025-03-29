from fastapi import FastAPI
from app.routes.auth_routes import router as auth_routes
from app.routes.docker_routes import router as docker_routes


app = FastAPI(title="Docker Container Management API")

app.include_router(auth_routes, prefix="/auth")
app.include_router(docker_routes, prefix="/docker")

@app.get("/")
def root():
    return {"message": "Docker Container Management System Running"}
