# agents/frontend_agent.py
import json
import re
from agents.base_agent import BaseAgent

class FrontendAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Senior Frontend Engineer и UI/UX Эксперт. Твоя задача: создавать "
            "полноценные, стильные и функциональные интерфейсы.\n\n"
            "ТВОИ ВОЗМОЖНОСТИ:\n"
            "1. ВИЗУАЛЬНЫЙ АНАЛИЗ: Если предоставлено изображение, ты должен в точности "
            "воспроизвести его стиль, сетку и эстетику в коде.\n"
            "2. ВЕРСТКА И СТИЛИ: Ты мастер CSS, Tailwind, SCSS. Создаешь адаптивные "
            "интерфейсы, которые идеально выглядят на всех устройствах.\n"
            "3. ИНТЕРАКТИВНОСТЬ: Ты пишешь чистый JavaScript/TypeScript, реализуешь "
            "состояния, анимации и бесшовную интеграцию с API.\n"
            "4. ШАБЛОНИЗАЦИЯ: Ты создаешь модульные компоненты, которые легко поддерживать.\n\n"
            "ПРАВИЛА ОТВЕТА:\n"
            "- Ответ должен быть в формате JSON, где ключи — пути к файлам, а значения — код.\n"
            "- Если ты создаешь новый стиль, обязательно включи конфигурацию (напр. tailwind.config.js).\n"
            "- Всегда сверяйся с контекстом бэкенда, чтобы имена полей в формах совпадали с API."
        )
        super().__init__(role_name="FrontendEngineer", system_prompt=system_prompt)

    def _extract_json(self, text: str) -> dict:
        """Извлекает JSON из ответа модели."""
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(text[start_idx:end_idx + 1])
            except:
                pass
        return {}

    def develop_ui(self, style_desc: str, project_context: str, image_paths: list = None) -> dict:
        """
        Создает или дорабатывает интерфейс на основе описания, картинок и контекста.
        """
        prompt = (
            f"ЗАДАЧА: Разработать/доработать фронтенд-часть проекта.\n"
            f"ТРЕБОВАНИЯ К СТИЛЮ: {style_desc}\n"
            f"КОНТЕКСТ ПРОЕКТА: {project_context}\n\n"
            "Проанализируй API бэкенда в контексте и создай полноценные страницы "
            "с версткой, стилями и JS-логикой. Верни ТОЛЬКО JSON с файлами."
        )
        
        response = self.ask_llm(prompt, context=project_context, images=image_paths)
        return self._extract_json(response)
