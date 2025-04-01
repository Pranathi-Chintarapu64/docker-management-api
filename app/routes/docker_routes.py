from fastapi import APIRouter, HTTPException, Form
import docker
import os
from typing import Optional

router = APIRouter()

# Docker client initialization
client = docker.from_env()

# Endpoint to build the Docker image
@router.post("/docker/build_image/")
async def build_image(
    image_name: str = Form(...),  # Image name from the form
    dockerfile_path: str = Form(...)  # Dockerfile path from the form
):
    try:
        # Check if the Dockerfile exists
        if not os.path.exists(dockerfile_path):
            raise HTTPException(status_code=400, detail="Dockerfile path does not exist.")
        
        context_path = os.path.dirname(dockerfile_path)  # Use directory of the Dockerfile as the context
        
        # Building the Docker image
        print(f"Building Docker image: {image_name} from Dockerfile: {dockerfile_path} with context: {context_path}")
        image,logs=client.images.build(path=os.path.dirname(dockerfile_path),dockerfile=os.path.basename(dockerfile_path),tag=image_name)



        
        # Returning logs or success response
        return {"message": f"Image {image_name} built successfully.", "logs": [log.get('stream') for log in logs if log.get('stream')]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building image: {str(e)}")


# Endpoint to run the Docker container
@router.post("/docker/run_container/")
async def run_container(
    image_name: str = Form(...),
    ports: str = Form(""),  # Default to empty string
    env_vars: str = Form(""),  # Default to empty string
    detached: bool = Form(True)
):
    try:
        port_mappings = {}
        if ports:
            for p in ports.split(","):
                if ":" in p:
                    host_port, container_port = p.split(":")
                    port_mappings[int(host_port)] = int(container_port)

        env_variables = {}
        if env_vars:
            for e in env_vars.split(","):
                if "=" in e:
                    key, value = e.split("=")
                    env_variables[key] = value

        container = client.containers.run(
            image_name,
            detach=detached,
            ports=port_mappings if port_mappings else None,
            environment=env_variables if env_variables else None
        )

        return {"message": "Container started successfully", "container_id": container.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running container: {str(e)}")


# Endpoint to check running containers
@router.get("/docker/containers_status/")
async def containers_status():
    try:
        containers = client.containers.list(all=True)  # Get all containers (running and stopped)
        container_data = []

        for container in containers:
            container_info = {
                "container_id": container.id,
                "container_name": container.name,
                "image_name": container.image.tags if container.image.tags else "No image name"
            }
            container_data.append(container_info)

        return {"containers": container_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching container status: {str(e)}")


# Endpoint to fetch logs of a container
@router.get("/docker/container_logs/{container_id}")
async def container_logs(container_id: str):
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=100).decode('utf-8')
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching container logs: {str(e)}")


# Endpoint to stop a running container
@router.post("/docker/stop_container/{container_id}")
async def stop_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"message": f"Container {container_id} stopped."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping container: {str(e)}")


# Endpoint to remove a container
@router.post("/docker/remove_container/{container_id}")
async def remove_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.remove()
        return {"message": f"Container {container_id} removed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing container: {str(e)}")


# Endpoint to create a Docker volume
@router.post("/docker/create_volume/")
async def create_volume(volume_name: str = Form(...)):
    try:
        volume = client.volumes.create(name=volume_name)
        return {"message": f"Volume {volume_name} created."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating volume: {str(e)}")
