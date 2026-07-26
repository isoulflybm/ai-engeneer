from agents.base_agent import BaseAgent


class QAEngineerAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Эксперт по обеспечению качества (QA) и отладке. "
            "Твоя задача: анализировать логи ошибок "
            "и сопоставлять их с текущим кодом проекта.\n"
            "ПРАВИЛА:\n"
            "1. Определи причину ошибки (Symptom -> Root Cause).\n"
            "2. Укажи конкретные файлы и строки кода, которые вызывают проблему.\n"
            "3. Сформулируй четкую инструкцию для Разработчика по исправлению.\n"
            "4. Ответ должен быть в формате:\n"
            "АНАЛИЗ: <описание ошибки>\n"
            "ИСПРАВЛЕНИЕ: <что нужно изменить в каких файлах>"
        )
        super().__init__(role_name="QA_Engineer", system_prompt=system_prompt)

    def analyze_error(self, logs: str, project_context: str) -> str:
        """Анализирует логи и контекст проекта."""
        prompt = (
            f"Логи запуска проекта:\n{logs}\n\n"
            "Пожалуйста, проанализируй ошибку и предложи исправление."
        )
        return self.ask_llm(prompt, context=project_context)
        
