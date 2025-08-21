import subprocess

# Example tool (add to agent.tools)
def git_diff() -> str:
    """Run git diff."""
    return subprocess.check_output(["git", "diff"]).decode()

# Add more tools as needed (e.g., apply_patch, read_file)