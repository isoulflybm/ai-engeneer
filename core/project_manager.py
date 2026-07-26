import os
from utils.file_handler import FileHandler
from utils.git_helper import GitHelper


class ProjectManager:
    def __init__(self, project_root: str):
        self.current_project_path = project_root
        self.file_handler = FileHandler()
        self.git_helper = GitHelper(project_root)

    def setup_project_structure(self):
        """Создает базовую структуру папок проекта."""
        folders = [
            'src',
            'logs',
            'docs',
        ]
        for folder in folders:
            os.makedirs(os.path.join(self.current_project_path, folder), exist_ok=True)

        self.git_helper.init_repo()
        print(f"Project structure created at {self.current_project_path}")

    def save_spec(self, spec_text: str):
        """Сохраняет ТЗ в файл project_spec.md."""
        path = os.path.join(self.current_project_path, "project_spec.md")
        self.file_handler.write_file(path, spec_text)
        self.git_helper.commit_changes("Initial project specification")

    def get_full_context(self) -> str:
        """Возвращает текущее состояние всего кода для передачи в LLM."""
        return self.file_handler.get_project_snapshot(self.current_project_path)

    def apply_code_change(self, relative_path: str, content: str, commit_message: str):
        """Применяет изменение кода в файл и фиксирует в Git."""
        full_path = os.path.join(self.current_project_path, relative_path)
        self.file_handler.write_file(full_path, content)
        self.git_helper.commit_changes(commit_message)
 
