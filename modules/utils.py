import os
import yaml
import json
from datetime import datetime

def load_config(config_path="config.yaml"):
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def load_last_execution(file_path="data/last_execution.json"):
    """Load the last execution details."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_last_execution(step_name, status, file_path="data/last_execution.json"):
    """Save the execution status of a step."""
    last_execution = load_last_execution(file_path)
    last_execution["last_run"] = datetime.now().isoformat()
    last_execution["steps"] = last_execution.get("steps", {})
    last_execution["steps"][step_name] = status

    with open(file_path, "w") as file:
        json.dump(last_execution, file, indent=4)

def get_task_name(config_task_name):
    """Generate or use the provided task name."""
    if config_task_name == "auto":
        return datetime.today().strftime('%Y%m%d')
    return config_task_name
