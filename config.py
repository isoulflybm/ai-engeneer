import os

# Настройки модели
MODEL_NAME = "gemma4:cloud"
CONTEXT_WINDOW = 256000
OLLAMA_BASE_URL = "http://localhost:11434"

# Пути
HOME_DIR = os.path.expanduser("~")
BASE_WORKSPACE = os.path.join(HOME_DIR, "ai_workspace")
PROJECTS_REGISTRY = os.path.join(BASE_WORKSPACE, "projects_registry.json")
LOG_FILE = os.path.join(BASE_WORKSPACE, "system_debug.log")

# Системные настройки
LOG_LEVEL = "INFO"
DEFAULT_ENCODING = "utf-8"

# Git настройки
GIT_COMMIT_TEMPLATE = "AI-Engineer: Step {step_number} - {task_description}"

# Настройки запуска проекта
DOCKER_RUN_COMMAND = "docker compose up --build"
# Если используете старый Docker Compose V1, замените на: "docker-compose up --build"
