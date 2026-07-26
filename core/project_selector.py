import json
import os
from config import PROJECTS_REGISTRY, BASE_WORKSPACE


class ProjectSelector:
    def __init__(self):
        os.makedirs(BASE_WORKSPACE, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self):
        if os.path.exists(PROJECTS_REGISTRY):
            with open(PROJECTS_REGISTRY, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_registry(self):
        with open(PROJECTS_REGISTRY, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)

    def list_projects(self):
        return list(self.registry.keys())

    def create_project(self, project_name: str) -> str:
        project_path = os.path.join(BASE_WORKSPACE, project_name)
        self.registry[project_name] = {
            "path": project_path,
            "description": "Created by AI-Engineer"
        }
        self._save_registry()
        return project_path

    def register_existing_project(self, project_name: str, project_path: str):
        """Добавляет уже существующую папку в реестр проектов."""
        self.registry[project_name] = {
            "path": project_path,
            "description": "Existing project imported"
        }
        self._save_registry()
        return project_path

    def get_project_path(self, project_name: str) -> str:
        return self.registry.get(project_name, {}).get("path")
        
