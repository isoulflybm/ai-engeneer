import os
from typing import List


class FileHandler:
    @staticmethod
    def write_file(path: str, content: str):
        """Записывает строку в файл, создавая папки если их нет."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def read_file(path: str) -> str:
        """Читает содержимое одного файла."""
        if not os.path.exists(path):
            return ""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def get_project_snapshot(root_dir: str,
                             ignored_dirs: List[str] = None) -> str:
        """
        Собирает 'слепок' проекта: обходит все файлы и объединяет их содержимое.
        Это то, что будет подаваться в контекст 256k Gemma 4.
        """
        if ignored_dirs is None:
            ignored_dirs = [
                '.git', '__pycache__', 'node_modules', '.venv', 'logs'
            ]

        snapshot = []
        for root, dirs, files in os.walk(root_dir):
            # Фильтруем игнорируемые папки
            dirs[:] = [d for d in dirs if d not in ignored_dirs]

            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.html', '.css',
                                  '.json', '.md', '.yml', '.yaml', '.php')):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, root_dir)

                    with open(full_path, 'r', encoding='utf-8',
                              errors='ignore') as f:
                        content = f.read()
                        snapshot.append(
                            f"--- FILE: {relative_path} ---\n{content}\n"
                        )

        return "\n".join(snapshot)
        
