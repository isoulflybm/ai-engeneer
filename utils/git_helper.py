import git
import os


class GitHelper:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.repo = None
        # Пытаемся открыть репозиторий только если папка существует
        if os.path.exists(self.project_root):
            try:
                self.repo = git.Repo(self.project_root)
            except git.InvalidGitRepositoryError:
                self.repo = None

    def init_repo(self):
        """Инициализирует новый git репозиторий."""
        os.makedirs(self.project_root, exist_ok=True)

        try:
            self.repo = git.Repo.init(self.project_root)
            print(f"Git repository initialized in {self.project_root}")
        except Exception as e:
            print(f"Error initializing git repo: {e}")

    def commit_changes(self, message: str):
        """Добавляет все изменения и делает коммит."""
        if self.repo:
            try:
                self.repo.git.add(A=True)
                self.repo.index.commit(message)
                print(f"Committed: {message}")
            except Exception as e:
                print(f"Commit failed: {e}")
        else:
            print("Git repo not initialized. Skipping commit.")

    def push_to_remote(self, remote_name="origin", branch="main"):
        if self.repo:
            try:
                self.repo.remotes[remote_name].push(branch)
                print(f"Pushed to {remote_name}/{branch}")
            except Exception as e:
                print(f"Push failed: {e}")
                
