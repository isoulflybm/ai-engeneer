from agents.base_agent import BaseAgent


class DocumentalistAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Профессиональный Технический Писатель. Твоя задача: создать качественную "
            "документацию к проекту на основе исходного кода и плана разработки.\n"
            "ПРАВИЛА:\n"
            "1. Пиши в формате Markdown.\n"
            "2. Документация должна включать: Описание проекта, Инструкцию по установке, "
            "Описание API/Функционала и примеры использования.\n"
            "3. Стиль должен быть строгим, техническим и понятным.\n"
            "4. Если в коде есть специфические настройки (Docker, env), обязательно отрази их."
        )
        super().__init__(role_name="Documentalist", system_prompt=system_prompt)

    def generate_docs(self, project_context: str, spec_text: str) -> str:
        """Генерирует README.md и документацию."""
        prompt = (
            f"Используя следующее ТЗ:\n{spec_text}\n\n"
            f"И текущий код проекта:\n{project_context}\n\n"
            "Создай полный README.md файл. Опиши, как запустить проект и как он работает."
        )
        return self.ask_llm(prompt)
        
