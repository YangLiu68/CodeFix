import subprocess

def run_command(command: str) -> str:
    """Executes a shell command and returns the output."""
    try:
        # For security, you might want to white-list commands or ask for confirmation
        # In this phase, we execute and catch output.
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Command failed with return code {result.returncode}:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
