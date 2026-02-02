from pathlib import Path
from typing import Dict


def get_module(base_dir="routes"):
    base_path = Path(base_dir)
    module = [
        p.name
        for p in base_path.iterdir()
        if p.is_dir() and not p.name.startswith("__") and not p.name.startswith(".")
    ]
    return module


def get_single_app_structure(base_dir: str = "applications") -> Dict[str, dict]:
    base_path = Path(base_dir)
    excluded_files = {"signals.py", "schemas.py", "services.py", "base.py"}
    all_model_files = []

    for app_dir in base_path.iterdir():
        if not app_dir.is_dir():
            continue

        model_files = [
            f"{base_dir}.{app_dir.name}.{file.stem}"
            for file in app_dir.glob("*.py")
            if file.is_file() and not file.name.startswith("__") and file.name not in excluded_files
        ]
        all_model_files.extend(model_files)

    all_model_files.append("aerich.models")
    return {
        "models": {
            "models": all_model_files,
            "default_connection": "default",
        }
    }
