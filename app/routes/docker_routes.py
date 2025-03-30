import docker
from fastapi import APIRouter, HTTPException

router = APIRouter()
client = docker.from_env()

@router.post("/docker/build_image/")
def build_image(dockerfile_path: str, tag: str):
    try:
        image, _ = client.images.build(path=dockerfile_path, tag=tag)
        return {"message": f"Image {tag} built successfully", "id": image.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/run_container/")
def run_container(image: str, name: str, detach: bool = True, ports: dict = None, env_vars: dict = None):
    try:
        container = client.containers.run(
            image=image,
            name=name,
            detach=detach,
            ports=ports,
            environment=env_vars
        )
        return {"message": f"Container {name} started successfully", "id": container.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker/running_containers/")
def running_containers():
    try:
        containers = client.containers.list()
        return [{"id": c.id, "name": c.name, "image": c.image.tags} for c in containers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docker/container_logs/{container_id}")
def container_logs(container_id: str):
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=100).decode('utf-8')
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/docker/stop_remove_container/{container_id}")
def stop_remove_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        return {"message": f"Container {container_id} stopped and removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker/create_volume/")
def create_volume(volume_name: str):
    try:
        volume = client.volumes.create(name=volume_name)
        return {"message": f"Volume {volume_name} created successfully", "id": volume.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


