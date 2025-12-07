import docker
import os
from hybrid_ai_assistant.config.config import config

client = docker.from_env()

def get_or_create_container(existing_id=None, run_id=None):
    # UPDATED: Check and reuse existing container if provided
    if existing_id:
        try:
            container = client.containers.get(existing_id)
            if container.status != 'running':
                container.start()
            return container.id
        except docker.errors.NotFound:
            pass  # Create new one below

    # Create new container
    # Ensure project dir exists
    # Use run_id to create an isolated workspace if provided, else root
    if run_id:
        workspace_host_path = os.path.join(config.PROJECT_DIR, run_id)
    else:
        workspace_host_path = config.PROJECT_DIR

    if not os.path.exists(workspace_host_path):
        try:
            os.makedirs(workspace_host_path)
        except Exception as e:
            print(f"Warning: Could not create project dir {workspace_host_path}: {e}")

    try:
        container = client.containers.run(
            config.DOCKER_IMAGE, 
            detach=True, 
            tty=True, # Keep it alive
            volumes={workspace_host_path: {'bind': '/workspace', 'mode': 'rw'}},
            working_dir='/workspace'
        )
        return container.id
    except Exception as e:
        print(f"Error starting container: {e}")
        return None

def exec_in_container(container_id: str, cmd: str):
    if not container_id:
        return "Error: No container ID provided."
    try:
        container = client.containers.get(container_id)
        # Verify container is running
        if container.status != 'running':
            container.start()
            
        result = container.exec_run(f"sh -c '{cmd}'")
        return result.output.decode()
    except Exception as e:
        return str(e)
