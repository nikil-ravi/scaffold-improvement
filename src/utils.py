from typing import Any, Dict
import docker
import os
import subprocess
import logging
import threading


def setup_docker() -> Any:
    """Setup and return Docker container."""
    client = docker.from_env()
    container = client.containers.run(
        "self-improve-agent",
        detach=True,
        volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
        working_dir="/app",
    )
    return container


def apply_patch(container: Any, patch: str) -> None:
    """Apply code patch in container."""
    patch_path = "/app/temp.patch"
    with open("temp.patch", "w") as f:
        f.write(patch)
    container.exec_run(["cp", "temp.patch", patch_path], workdir="/app")
    result = container.exec_run(["git", "apply", patch_path], workdir="/app")
    if result.exit_code != 0:
        output = result.output.decode()
        safe_log(f"Failed to apply patch: {output}")
        raise subprocess.CalledProcessError(result.exit_code, "git apply", output=output)


def get_logs(eval_results: Dict) -> str:
    """Get evaluation logs (mock)."""
    return str(eval_results)


def safe_log(message: str, level: int = logging.INFO) -> None:
    """Thread-safe logging."""
    logger = logging.getLogger(f"Agent-{threading.get_ident()}")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.log(level, message)