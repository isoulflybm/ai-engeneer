import os
import sys
from config import PROJECTS_REGISTRY, BASE_WORKSPACE, LOG_FILE

from utils.logger import setup_logger
from core.project_selector import ProjectSelector
from core.project_manager import ProjectManager
from core.state_manager import StateManager
from core.executor import Executor

from agents.architect import ArchitectAgent
from agents.developer import DeveloperAgent
from agents.qa_engineer import QAEngineerAgent
from agents.documentalist import DocumentalistAgent
from agents.auditor import AuditorAgent


def main():
    # Инициализация логгера
    setup_logger()

    # Выбор проекта
    selector = ProjectSelector()

    # Авто-регистрация существующего проекта
    old_project_name = "ai_engineer_project"
    old_project_path = os.path.join(BASE_WORKSPACE, old_project_name)
    if old_project_name not in selector.list_projects() and os.path.exists(old_project_path):
        print(f"📦 Обнаружен существующий проект: {old_project_name}. Добавляю в реестр...")
        selector.register_existing_project(old_project_name, old_project_path)

    print("\n--- ДОБРО ПОЖАЛОВАТЬ В AI ENGINEER ---")
    projects = selector.list_projects()

    if projects:
        print("\nДоступные проекты:")
        for i, name in enumerate(projects, 1):
            print(f"{i}. {name}")
        print(f"{len(projects) + 1}. [Создать новый проект]")

        choice = input("\nВыберите проект или введите цифру для создания нового: ")

        if choice.isdigit() and int(choice) <= len(projects):
            project_name = projects[int(choice) - 1]
            project_root = selector.get_project_path(project_name)
            print(f"Загрузка проекта: {project_name}")
        else:
            project_name = input("Введите название нового проекта: ")
            project_root = selector.create_project(project_name)
    else:
        project_name = input("Проектов нет. Введите название для первого проекта: ")
        project_root = selector.create_project(project_name)

    # Инициализация менеджеров
    pm = ProjectManager(project_root)
    sm = StateManager(project_root)
    sm.load_state()
    executor = Executor(project_root)

    # Инициализация агентов
    architect = ArchitectAgent()
    developer = DeveloperAgent()
    qa_engineer = QAEngineerAgent()
    documentalist = DocumentalistAgent()
    auditor = AuditorAgent()

    # Главный цикл
    while True:
        print("\n" + "=" * 40)
        print(" 🤖 AI ENGINEER FRAMEWORK v1.0")
        print("=" * 40)
        print("1. [Init]    - Инициализация проекта и ТЗ")
        print("2. [Plan]    - Создание плана разработки")
        print("3. [Develop] - Реализация текущего шага плана")
        print("4. [Test]    - Запуск в Docker и проверка")
        print("5. [Debug]   - Анализ ошибок и исправление")
        print("6. [Docs]    - Генерация документации")
        print("7. [Audit]   - Сверка реализации с ТЗ")
        print("8. [EditSpec]- Редактирование ТЗ и перезапуск аудита")
        print("0. [Exit]    - Выход из системы")
        print("=" * 40)

        choice = input("\nВыберите режим: ")

        try:
            # ============================================================
            # РЕЖИМ 1: Init
            # ============================================================
            if choice == "1":
                print("\n--- Инициализация ---")
                spec = input("Введите подробное ТЗ вашего проекта: ")
                pm.setup_project_structure()
                pm.save_spec(spec)
                print("✅ Структура создана, ТЗ сохранено в project_spec.md")

            # ============================================================
            # РЕЖИМ 2: Plan
            # ============================================================
            elif choice == "2":
                print("\n--- Планирование ---")
                spec_text = pm.file_handler.read_file(
                    os.path.join(pm.current_project_path, "project_spec.md")
                )
                if not spec_text:
                    print("❌ Ошибка: Сначала запустите Init.")
                    continue

                print("🧠 Архитектор проектирует систему...")
                plan = architect.create_plan(spec_text)
                if plan:
                    sm.save_plan(plan)
                    print(f"✅ План создан! Всего шагов: {len(plan)}")
                    for s in plan:
                        print(f"  {s['step']}. {s['task']}")
                else:
                    print("❌ Ошибка при генерации плана.")

            # ============================================================
            # РЕЖИМ 3: Develop
            # ============================================================
            elif choice == "3":
                print("\n--- Разработка ---")
                current_step = sm.get_current_step()
                if not current_step:
                    print("✅ Все задачи выполнены или план отсутствует.")
                    continue

                print(f"🛠 Работа над шагом {current_step['step']}: {current_step['task']}...")
                context = pm.get_full_context()
                code_changes = developer.develop_step(current_step, context)

                if code_changes:
                    for rel_path, content in code_changes.items():
                        full_path = os.path.join(pm.current_project_path, rel_path)
                        print(f"DEBUG: Записываю файл в {full_path}")
                        pm.apply_code_change(
                            rel_path, content,
                            f"Step {current_step['step']}"
                        )

                    step_index = current_step['step'] - 1
                    sm.update_step(step_index)
                    print("✅ Код применен и закоммичен.")
                else:
                    print("❌ Разработчик не смог создать код.")

            # ============================================================
            # РЕЖИМ 4: Test
            # ============================================================
            elif choice == "4":
                print("\n--- Тестирование ---")
                if executor.run_docker_compose():
                    print("✅ Проект успешно запущен в контейнере!")
                    
                    # Проверка Swagger
                    print("🔍 Проверка доступности Swagger API...")
                    swagger_url = executor.check_swagger_availability()
                    if swagger_url != "NOT_FOUND":
                        print(f"🌟 Документация Swagger доступна по адресу: {swagger_url}")
                    else:
                        print("⚠️  Swagger не обнаружен или сервер еще запускается.")
                        print(f"Попробуйте проверить вручную: http://localhost:8000/docs")
                else:
                    print("❌ Ошибка при запуске. Используйте режим [Debug].")

            # ============================================================
            # РЕЖИМ 5: Debug
            # ============================================================
            elif choice == "5":
                print("\n--- Отладка ---")
                logs = executor.get_last_logs()
                context = pm.get_full_context()

                print("🔍 QA-инженер изучает логи...")
                analysis = qa_engineer.analyze_error(logs, context)
                print(f"\n{analysis}\n")

                if input("Исправить ошибку? (y/n): ").lower() == 'y':
                    debug_step = {
                        "step": "DEBUG",
                        "task": f"Fix: {analysis}",
                        "files": []
                    }
                    code_changes = developer.develop_step(debug_step, context)
                    if code_changes:
                        for rel_path, content in code_changes.items():
                            pm.apply_code_change(rel_path, content, "Bugfix")
                        print("✅ Исправления внесены.")
                    else:
                        print("❌ Не удалось создать исправление.")

            # ============================================================
            # РЕЖИМ 6: Docs
            # ============================================================
            elif choice == "6":
                print("\n--- Документирование ---")
                spec_text = pm.file_handler.read_file(
                    os.path.join(pm.current_project_path, "project_spec.md")
                )
                context = pm.get_full_context()

                print("📝 Техписатель готовит документацию...")
                readme_content = documentalist.generate_docs(context, spec_text)
                pm.apply_code_change("README.md", readme_content, "Generate documentation")
                print("✅ README.md успешно создан в корне проекта.")

            # ============================================================
            # РЕЖИМ 7: Audit
            # ============================================================
            elif choice == "7":
                print("\n--- Аудит проекта ---")
                spec_text = pm.file_handler.read_file(
                    os.path.join(pm.current_project_path, "project_spec.md")
                )
                plan_data = sm.get_all_steps()
                context = pm.get_full_context()

                print("🧐 Аудитор сверяет код с ТЗ...")
                result = auditor.audit_project(spec_text, plan_data, context)

                if "error" not in result:
                    print(f"\n📊 Готовность: {result['readiness_percentage']}%")

                    # Вывод таблицы требований, если есть
                    req_table = result.get("requirements_table", [])
                    if req_table:
                        print("\n📋 Таблица соответствия:")
                        print("-" * 70)
                        for row in req_table:
                            status_icon = "✅" if row.get("implemented") else "❌"
                            print(f"  {status_icon} {row['requirement']}")
                            if not row.get("implemented"):
                                print(f"     ↳ Отсутствует!")
                            else:
                                print(f"     ↳ {row.get('location', '—')}")
                        print("-" * 70)

                    print(f"\n📝 Анализ:\n{result['analysis']}")

                    extra = result.get("additional_steps", [])
                    if extra:
                        print(f"\n⚠️  Найдено {len(extra)} нереализованных требований:")
                        for s in extra:
                            print(f"  → {s['task']}")
                        if input("\nДобавить в план? (y/n): ").lower() == 'y':
                            sm.append_steps(extra)
                            print("✅ План дополнен. Возвращайтесь в Режим 3 (Develop).")
                    else:
                        print("✅ Проект полностью соответствует ТЗ!")
                else:
                    print(f"❌ {result.get('error')}")
                    if "raw" in result:
                        print(f"Сырой ответ модели:\n{result['raw']}")

            # ============================================================
            # РЕЖИМ 8: EditSpec
            # ============================================================
            elif choice == "8":
                print("\n--- Редактирование ТЗ ---")
                spec_path = os.path.join(pm.current_project_path, "project_spec.md")
                old_spec = pm.file_handler.read_file(spec_path)

                print("📄 ТЕКУЩЕЕ ТЗ:")
                print("-" * 50)
                print(old_spec)
                print("-" * 50)

                print("\nВыберите действие:")
                print("1. Заменить ТЗ полностью (вставить новый текст)")
                print("2. Дополнить ТЗ (добавить требования в конец)")
                print("3. Отмена")

                edit_choice = input("\nВаш выбор: ")

                if edit_choice == "3":
                    continue

                if edit_choice == "1":
                    new_spec = input("\nВведите новое ТЗ полностью:\n")
                    pm.file_handler.write_file(spec_path, new_spec)
                    pm.git_helper.commit_changes("Updated project specification (replaced)")

                elif edit_choice == "2":
                    print("Введите дополнительные требования (для завершения — пустая строка или 'END'):")
                    addition_lines = []
                    while True:
                        line = input()
                        if line.strip() == "" or line.strip().upper() == "END":
                            break
                        addition_lines.append(line)
                    addition = "\n".join(addition_lines)

                    if addition.strip():
                        new_spec = old_spec + "\n\n### Дополнительные требования\n" + addition
                        pm.file_handler.write_file(spec_path, new_spec)
                        pm.git_helper.commit_changes("Updated project specification (appended requirements)")
                        print("✅ Требования добавлены в ТЗ.")
                    else:
                        print("⚠️ Ничего не добавлено.")
                        continue

                else:
                    print("Неверный выбор.")
                    continue

                # Автоматически предлагаем запустить аудит
                if input("\nЗапустить аудит с обновлённым ТЗ? (y/n): ").lower() == 'y':
                    print("\n🧐 Аудитор сверяет код с обновлённым ТЗ...")
                    updated_spec = pm.file_handler.read_file(spec_path)
                    plan_data = sm.get_all_steps()
                    context = pm.get_full_context()

                    result = auditor.audit_project(updated_spec, plan_data, context)

                    if "error" not in result:
                        print(f"\n📊 Готовность: {result['readiness_percentage']}%")

                        req_table = result.get("requirements_table", [])
                        if req_table:
                            print("\n📋 Таблица соответствия:")
                            print("-" * 70)
                            for row in req_table:
                                status_icon = "✅" if row.get("implemented") else "❌"
                                print(f"  {status_icon} {row['requirement']}")
                                if not row.get("implemented"):
                                    print(f"     ↳ Отсутствует!")
                                else:
                                    print(f"     ↳ {row.get('location', '—')}")
                            print("-" * 70)

                        print(f"\n📝 Анализ:\n{result['analysis']}")

                        extra = result.get("additional_steps", [])
                        if extra:
                            print(f"\n⚠️  Найдено {len(extra)} нереализованных требований:")
                            for s in extra:
                                print(f"  → {s['task']}")
                            if input("\nДобавить в план? (y/n): ").lower() == 'y':
                                sm.append_steps(extra)
                                print("✅ План дополнен. Возвращайтесь в Режим 3 (Develop).")
                        else:
                            print("✅ Проект полностью соответствует новым требованиям!")
                    else:
                        print(f"❌ Аудитор не смог дать структурированный ответ: {result.get('error')}")
                        if input("Перегенерировать план через Архитектора? (y/n): ").lower() == 'y':
                            print("🧠 Архитектор пересматривает план...")
                            plan = architect.create_plan(updated_spec)
                            if plan:
                                sm.save_plan(plan)
                                print(f"✅ План пересоздан! Всего шагов: {len(plan)}")
                                for s in plan:
                                    print(f"  {s['step']}. {s['task']}")

            # ============================================================
            # РЕЖИМ 0: Exit
            # ============================================================
            elif choice == "0":
                print("Завершение работы. Удачи в разработке!")
                break

            else:
                print("Неверный ввод. Выберите число от 0 до 8.")

        except Exception as e:
            print(f"💥 Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
    
