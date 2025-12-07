import docker
import os
from hybrid_ai_assistant.config.config import config

client = docker.from_env()

def get_or_create_container():
    # Check if running, else create with volume mount: host PROJECT_DIR -> /workspace
    # Ensure project dir exists
    if not os.path.exists(config.PROJECT_DIR):
        try:
            os.makedirs(config.PROJECT_DIR)
        except Exception as e:
            print(f"Warning: Could not create project dir {config.PROJECT_DIR}: {e}")

    # Simple logic: create a new one every time or reuse if we had a persistent name. 
    # For now, following user snippet, we just run one.
    try:
        # In a real app we might name it or tag it to reuse
        container = client.containers.run(
            config.DOCKER_IMAGE, 
            detach=True, 
            tty=True, # Keep it alive
            volumes={config.PROJECT_DIR: {'bind': '/workspace', 'mode': 'rw'}},
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
