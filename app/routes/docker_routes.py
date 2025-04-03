from fastapi import APIRouter, HTTPException, Form, Depends
import docker
import os
from typing import Optional
from app.auth import get_current_user

router = APIRouter()

# Docker client initialization
client = docker.from_env()

# Endpoint to build the Docker image
@router.post("/docker/build_image/")
async def build_image(
    image_name: str = Form(...),  # Image name from the form
    dockerfile_path: str = Form(...),  # Dockerfile path from the form
    user: dict = Depends(get_current_user)  # Require authentication
):
    try:
        if not os.path.exists(dockerfile_path):
            raise HTTPException(status_code=400, detail="Dockerfile path does not exist.")
        
        context_path = os.path.dirname(dockerfile_path)
        image, logs = client.images.build(path=os.path.abspath(dockerfile_path), tag=image_name)

        return {"message": f"Image {image_name} built successfully.", "logs": [log.get('stream') for log in logs if log.get('stream')]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building image: {str(e)}")

# Endpoint to run a Docker container
@router.post("/docker/run_container/")
async def run_container(
    image_name: str = Form(...),
    ports: str = Form(""),
    env_vars: str = Form(""),
    detached: bool = Form(True),
    user: dict = Depends(get_current_user)  # Require authentication
):
    try:
        port_mappings = {int(hp): int(cp) for p in ports.split(",") if ":" in p for hp, cp in [p.split(":")]}
        env_variables = {k: v for e in env_vars.split(",") if "=" in e for k, v in [e.split("=")]} 
        container = client.containers.run(
            image_name,
            detach=detached,
            ports=port_mappings or None,
            environment=env_variables or None
        )
        return {"message": "Container started successfully", "container_id": container.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running container: {str(e)}")

# Endpoint to check running containers
@router.get("/docker/containers_status/")
async def containers_status(user: dict = Depends(get_current_user)):  # Require authentication
    try:
        containers = client.containers.list(all=True)
        return {"containers": [{"container_id": c.id, "container_name": c.name, "image_name": c.image.tags or "No image"} for c in containers]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching container status: {str(e)}")

# Endpoint to fetch logs of a container
@router.get("/docker/container_logs/{container_id}")
async def container_logs(container_id: str, user: dict = Depends(get_current_user)):  # Require authentication
    try:
        container = client.containers.get(container_id)
        return {"logs": container.logs(tail=100).decode('utf-8')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching container logs: {str(e)}")

# Endpoint to stop a running container
@router.post("/docker/stop_container/{container_id}")
async def stop_container(container_id: str, user: dict = Depends(get_current_user)):  # Require authentication
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"message": f"Container {container_id} stopped."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping container: {str(e)}")

# Endpoint to remove a container
@router.post("/docker/remove_container/{container_id}")
async def remove_container(container_id: str, user: dict = Depends(get_current_user)):  # Require authentication
    try:
        container = client.containers.get(container_id)
        container.remove()
        return {"message": f"Container {container_id} removed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing container: {str(e)}")

# Endpoint to create a Docker volume
@router.post("/docker/create_volume/")
async def create_volume(volume_name: str = Form(...), user: dict = Depends(get_current_user)):  # Require authentication
    try:
        volume = client.volumes.create(name=volume_name)
        return {"message": f"Volume {volume_name} created."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating volume: {str(e)}")









@router.get("/containers_status/")
def get_containers_status(current_user: dict = Depends(get_current_user)):  # Enforce auth
    # Now only authenticated users can access this!
    containers = get_all_containers()  # Fetch container info
    return {"containers": containers}
