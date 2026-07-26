# agents/architect.py
import json
from agents.base_agent import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Главный Системный Архитектор. Твоя задача: проанализировать ТЗ и составить "
            "детальный, атомарный план разработки проекта.\n"
            "ПРАВИЛА:\n"
            "1. Каждый шаг должен быть максимально простым (один файл или одна функция).\n"
            "2. ОБЯЗАТЕЛЬНО: если проект содержит API, первым шагом или одним из первых "
            "должно быть проектирование эндпоинтов и настройка Swagger/OpenAPI документации.\n"
            "3. Ответ должен быть СТРОГО в формате JSON списка объектов.\n"
            "4. Пример формата:\n"
            '[{"step": 1, "task": "Настроить базовый сервер FastAPI с автоматической генерацией Swagger", '
            '"files": ["src/main.py"], "status": "pending"}]\n'
            "5. При описании путей используй ТОЛЬКО прямые слэши (/), "
            "избегай одиночных обратных слэшей (\\) внутри текстовых полей."
        )
        super().__init__(role_name="Architect", system_prompt=system_prompt)

    def create_plan(self, project_spec: str) -> list:
        """Превращает ТЗ в JSON-план."""
        prompt = (
            f"Проанализируй следующее ТЗ и составь план разработки. "
            f"Если в ТЗ есть работа с данными или внешними запросами, обязательно включи "
            f"создание интерактивной документации Swagger:\n\n"
            f"{project_spec}\n\nВерни только JSON список."
        )
        response = self.ask_llm(prompt)
        clean_response = response.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            print("Ошибка: Архитектор вернул некорректный JSON.")
            return []
