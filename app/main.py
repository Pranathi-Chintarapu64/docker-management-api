from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, docker_routes

app = FastAPI()

# CORS Middleware - Allow all origins (you can adjust this as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace * with specific URLs like ["http://localhost"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes
app.include_router(auth_routes.router)
app.include_router(docker_routes.router)
