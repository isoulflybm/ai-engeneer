# agents/designer.py
from agents.base_agent import BaseAgent

class DesignerAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "Ты — Senior UI/UX Designer и Frontend-архитектор. Твоя задача: создавать "
            "визуальную концепцию интерфейса и переводить её в конкретный код стилей.\n"
            "ПРАВИЛА:\n"
            "1. Если тебе предоставлено изображение, проанализируй: цветовую гамму, "
            "отступы (spacing), радиусы скругления, шрифты и общую композицию.\n"
            "2. Ты должен выдать конкретный технический результат: "
            "   - Конфигурацию Tailwind CSS (tailwind.config.js).\n"
            "   - Глобальный CSS файл (globals.css) с переменными цветов.\n"
            "   - Структуру основных компонентов (UI Kit).\n"
            "3. Твои решения должны быть современными, адаптивными и доступными (WCAG).\n"
            "4. Если описание текстовое, предложи 2-3 варианта цветовых схем перед финальным кодом."
        )
        super().__init__(role_name="Designer", system_prompt=system_prompt)

    def design_interface(self, style_description: str, project_context: str, image_paths: list = None) -> str:
        """Создает дизайн-систему на основе текста и/или картинок."""
        prompt = (
            f"ЗАДАЧА: Разработать стилизацию фронтенда.\n"
            f"ОПИСАНИЕ СТИЛЯ: {style_description}\n\n"
            f"Основываясь на этом, создай полную дизайн-систему (цвета, шрифты, компоненты), "
            f"которую разработчик сможет внедрить в проект. "
            f"Если есть изображения, строго следуй их визуальному языку."
        )
        return self.ask_llm(prompt, context=project_context, images=image_paths)
