import docker

client = docker.from_env()

def build_image(dockerfile_path: str, tag: str):
    """Builds a Docker image from a given Dockerfile path and assigns a tag."""
    try:
        image, logs = client.images.build(path=dockerfile_path, tag=tag)
        return {"status": "success", "image_id": image.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_container(image: str, name: str, ports: dict, env_vars: dict, detach: bool = True):
    """Runs a container with the given parameters."""
    try:
        container = client.containers.run(
            image, 
            name=name, 
            ports=ports, 
            environment=env_vars, 
            detach=detach
        )
        return {"status": "success", "container_id": container.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_running_containers():
    """Fetches all currently running containers."""
    containers = client.containers.list()
    return [{"id": c.id, "name": c.name, "image": c.image.tags} for c in containers]

def get_container_logs(container_id: str):
    """Fetches the last 100 lines of logs from a container."""
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=100).decode("utf-8")
        return {"status": "success", "logs": logs}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def stop_and_remove_container(container_id: str):
    """Stops and removes a container by ID."""
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        return {"status": "success", "message": f"Container {container_id} removed."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_named_volume(volume_name: str):
    """Creates a named Docker volume."""
    try:
        volume = client.volumes.create(name=volume_name)
        return {"status": "success", "volume_name": volume.name}
    except Exception as e:
        return {"status": "error", "message": str(e)}
