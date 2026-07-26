import json
import os


class StateManager:
    def __init__(self, project_root: str):
        self.plan_path = os.path.join(project_root, "development_plan.json")
        self.state = {
            "current_step": 0,
            "steps": [],
            "status": "initialized"
        }

    def save_plan(self, plan_data: list):
        """Сохраняет список шагов, сгенерированный Архитектором."""
        self.state["steps"] = plan_data
        self.state["current_step"] = 0
        self._write_to_disk()

    def update_step(self, step_index: int, status: str = "completed"):
        """Обновляет статус конкретного шага и сдвигает текущий указатель."""
        if 0 <= step_index < len(self.state["steps"]):
            self.state["steps"][step_index]["status"] = status
            self.state["current_step"] = step_index + 1
            self._write_to_disk()

    def get_current_step(self):
        """Возвращает данные о текущем активном шаге."""
        idx = self.state["current_step"]
        if idx < len(self.state["steps"]):
            return self.state["steps"][idx]
        return None

    def get_all_steps(self):
        return self.state["steps"]

    def append_steps(self, new_steps: list):
        """Добавляет новые шаги в конец существующего плана."""
        start_step = len(self.state["steps"]) + 1
        for i, step in enumerate(new_steps):
            step["step"] = start_step + i
            self.state["steps"].append(step)
        self._write_to_disk()
        print(f"✅ Добавлено {len(new_steps)} новых шагов в план.")

    def _write_to_disk(self):
        with open(self.plan_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def load_state(self):
        """Загружает состояние из файла, если он существует."""
        if os.path.exists(self.plan_path):
            try:
                with open(self.plan_path, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка чтения development_plan.json: {e}")
                print("Попробуйте вручную исправить ошибки в JSON-файле "
                      "или удалите его для перегенерации плана.")
                      
