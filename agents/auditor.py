import json
import re
from agents.base_agent import BaseAgent
from utils.logger import get_logger


logger = get_logger("AuditorAgent")


class AuditorAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Строгий Технический Аудитор. Никаких общих фраз. Только факты.\n\n"
            "АЛГОРИТМ (выполняй ПОШАГОВО, не пропуская ни одного пункта):\n\n"
            "ШАГ 1. Выпиши ВСЕ функциональные требования из ТЗ в виде плоского списка.\n"
            "   — Каждый эндпоинт = отдельное требование.\n"
            "   — Каждая «фича» = отдельное требование.\n"
            "   Пример: «POST /train/upload», «POST /search/image», "
            "«HTML-интерфейс с веб-камерой».\n\n"
            "ШАГ 2. Для КАЖДОГО требования из шага 1 проверь наличие в коде.\n"
            "   — Для эндпоинтов: ИЩИ КОНКРЕТНЫЙ декоратор "
            "(@router.post, @app.post и т.д.) с нужным путём.\n"
            "   — Для фронтенда: ИЩИ вызовы fetch() или формы с соответствующим URL.\n"
            "   — Если требование про «поиск по веб-камере», в коде должен быть "
            "ОБРАБОТЧИК /search/stream, а НЕ только /search/video.\n\n"
            "ШАГ 3. Составь ТАБЛИЦУ. Каждая строка: требование | ДА/НЕТ | "
            "где именно в коде.\n\n"
            "ШАГ 4. Для каждого НЕТ создай ОТДЕЛЬНЫЙ дополнительный шаг.\n\n"
            "ШАГ 5. Посчитай процент: (количество ДА / общее количество требований) × 100.\n\n"
            "ВАЖНО:\n"
            "— Если эндпоинт вызывается фронтендом, но отсутствует в бэкенде — это НЕТ.\n"
            "— Если эндпоинт есть в бэкенде, но не используется фронтендом — "
            "это тоже пробел, отметь его.\n"
            "— НЕ ПИШИ «код полностью соответствует», если есть хотя бы одно НЕТ.\n\n"
            "ФОРМАТ ОТВЕТА — ТОЛЬКО JSON:\n"
            '{\n'
            '  "readiness_percentage": 85,\n'
            '  "requirements_table": [\n'
            '    {"requirement": "POST /train/upload", "implemented": true, '
            '"location": "routes/train.py:42"},\n'
            '    {"requirement": "POST /search/stream", "implemented": false, '
            '"location": "ОТСУТСТВУЕТ"}\n'
            '  ],\n'
            '  "analysis": "Краткий вывод: что именно не реализовано и почему",\n'
            '  "additional_steps": [\n'
            '    {"step": 99, "task": "Добавить эндпоинт POST /search/stream '
            'в routes/search.py", '
            '"files": ["routes/search.py"], "status": "pending"}\n'
            '  ]\n'
            '}'
        )
        super().__init__(role_name="Auditor", system_prompt=system_prompt)

    def _extract_json(self, text: str) -> dict:
        """Извлекает JSON из ответа модели."""
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return {}

    def audit_project(self, spec_text: str, plan_data: list,
                      project_context: str) -> dict:
        # Обрезаем контекст до разумного размера, чтобы модель не теряла фокус
        truncated_context = project_context[:80000]
        if len(project_context) > 80000:
            truncated_context += "\n\n... (контекст обрезан для фокусировки) ..."

        prompt = (
            f"=== ТЗ (ИСТОЧНИК ИСТИНЫ) ===\n{spec_text}\n\n"
            f"=== ПЛАН (запланированные шаги) ===\n"
            f"{json.dumps(plan_data, ensure_ascii=False)}\n\n"
            f"=== КОД (фактическая реализация) ===\n{truncated_context}\n\n"
            "Выполни СТРОГО по алгоритму: выпиши ВСЕ требования → "
            "проверь КАЖДОЕ в коде → "
            "составь таблицу → найди все НЕТ → посчитай процент. Верни ТОЛЬКО JSON."
        )
        response = self.ask_llm(prompt, context=truncated_context)
        logger.debug(f"Audit response:\n{response}")

        result = self._extract_json(response)

        if not result or "error" in result:
            # Запасной вариант: просим ещё раз, но короче
            retry_prompt = (
                "Кратко: перечисли ВСЕ эндпоинты, которые должны быть согласно ТЗ. "
                "Для каждого скажи ДА (реализован) или НЕТ (отсутствует). "
                "Верни ТОЛЬКО JSON."
            )
            retry_response = self.ask_llm(retry_prompt, context=truncated_context)
            result = self._extract_json(retry_response)

        if not result:
            result = {
                "error": "Не удалось извлечь JSON из ответа",
                "raw": response[:500]
            }

        return result
        
