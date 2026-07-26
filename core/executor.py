import subprocess
import os
import requests  # Добавляем импорт requests
from config import DOCKER_RUN_COMMAND, SWAGGER_ENDPOINTS, DEFAULT_API_PORT

class Executor:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.log_path = os.path.join(self.project_root, "logs/test_run.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def run_docker_compose(self) -> bool:
        """Запускает команду из конфига."""
        print(f"🚀 Запуск проекта командой: {DOCKER_RUN_COMMAND}...")
        try:
            process = subprocess.run(
                DOCKER_RUN_COMMAND,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(process.stdout)
                f.write("\n--- STDERR ---\n")
                f.write(process.stderr)

            return process.returncode == 0

        except subprocess.TimeoutExpired:
            print("❌ Ошибка: Тайм-аут при запуске контейнера.")
            return False
        except Exception as e:
            print(f"❌ Критическая ошибка выполнения: {e}")
            return False

    def check_swagger_availability(self) -> str:
        """
        Проверяет доступность Swagger UI.
        Возвращает URL, если найден, или сообщение об ошибке.
        """
        # В реальном сценарии порт может быть в docker-compose.yml, 
        # здесь используем DEFAULT_API_PORT для базовой проверки.
        base_url = f"http://localhost:{DEFAULT_API_PORT}"
        
        for endpoint in SWAGGER_ENDPOINTS:
            try:
                full_url = base_url + endpoint
                response = requests.get(full_url, timeout=5)
                if response.status_code == 200:
                    return full_url
            except requests.RequestException:
                continue
        
        return "NOT_FOUND"

    def get_last_logs(self) -> str:
        """Читает лог последнего запуска."""
        if os.path.exists(self.log_path):
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "Логи отсутствуют."
