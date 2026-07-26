import json
import re
from agents.base_agent import BaseAgent
from utils.logger import get_logger


logger = get_logger("DeveloperAgent")


class DeveloperAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Senior Fullstack Разработчик. Твоя задача: реализовать конкретный шаг "
            "плана разработки.\n"
            "ОТВЕТ ДОЛЖЕН БЫТЬ ТОЛЬКО В ФОРМАТЕ JSON.\n"
            "ПРАВИЛА:\n"
            "1. Используй предоставленный контекст всех файлов проекта.\n"
            "2. СТАНДАРТ API: Если ты создаешь серверную часть, используй фреймворки с поддержкой "
            "автоматического Swagger (например, FastAPI для Python). Эндпоинты должны иметь "
            "четкие типы данных, описания и примеры, чтобы Swagger был информативным.\n"
            "3. Ключи JSON — относительные пути к файлам, значения — полный код этого файла.\n"
            "4. Если файл нужно обновить, переписывай его ПОЛНОСТЬЮ.\n"
            "5. При описании путей используй ТОЛЬКО прямые слэши (/).\n"
            "ФОРМАТ ОТВЕТА:\n"
            '{\n  "src/main.py": "код файла...",\n  "requirements.txt": "код файла..."\n}'
        )
        super().__init__(role_name="Developer", system_prompt=system_prompt)

    def _extract_json(self, text: str) -> dict:
        """
        Продвинутый метод извлечения JSON из ответа модели.
        """
        # 1. Убираем Markdown-блоки
        text = re.sub(r'```json\s*|\s*```', '', text)
        text = text.strip()

        # 2. Ищем первую '{' и последнюю '}'
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Попытка исправить одиночные кавычки
                try:
                    return json.loads(json_str.replace("'", '"'))
                except json.JSONDecodeError:
                    pass
        return {}

    def develop_step(self, step_data: dict, project_context: str) -> dict:
        """
        Генерирует код для конкретного шага.
        """
        prompt = (
            f"ТЕКУЩИЙ ШАГ: {step_data['step']}\n"
            f"ЗАДАЧА: {step_data['task']}\n"
            f"ФАЙЛЫ: {step_data.get('files', 'определи сам')}\n\n"
            "ВЕРНИ ТОЛЬКО JSON ОБЪЕКТ."
        )

        response = self.ask_llm(prompt, context=project_context)
        logger.debug(f"Ответ от LLM для шага {step_data['step']}:\n{response}")

        return self._extract_json(response)
        
