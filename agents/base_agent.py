# agents/base_agent.py
import ollama
from config import MODEL_NAME, OLLAMA_BASE_URL

class BaseAgent:
    def __init__(self, role_name: str, system_prompt: str):
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.client = ollama.Client(host=OLLAMA_BASE_URL)

    def ask_llm(self, prompt: str, context: str = "", images: list = None) -> str:
        """
        Метод для взаимодействия с Gemma 4.
        images: список путей к файлам изображений.
        """
        full_prompt = f"System Role: {self.system_prompt}\n\n"
        if context:
            full_prompt += f"Project Context:\n{context}\n\n---\n"
        full_prompt += f"Current Task: {prompt}"

        try:
            # Если переданы изображения, Ollama ожидает их в параметре images
            response = self.client.chat(
                model=MODEL_NAME,
                messages=[{
                    'role': 'user', 
                    'content': full_prompt, 
                    'images': images # Передаем список путей или base64
                }],
                options={
                    'num_ctx': 256000,
                    'temperature': 0.4, # Немного повышаем для креативности в дизайне
                }
            )
            return response['message']['content']
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
