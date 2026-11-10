from pathlib import Path

from application.network_service import NetworkService
from domain.models import NetworkError, TYPES


def run(service: NetworkService):
    while True:
        try:
            print("\n1. Создать  2. Список  3. Изменить  4. Удалить"
                  "\n5. Сохранить  6. Загрузить  0. Выход")
            choice = input("Действие: ").strip()
            if choice == "0":
                return
            if choice in ("5", "6"):
                path = Path(input("Путь к файлу: ").strip())
                if choice == "5":
                    service.save(path)
                else:
                    service.load(path)
                print("Готово")
                continue
            if choice not in ("1", "2", "3", "4"):
                raise NetworkError("Выбери действие из меню")
            kind = input("Тип (users, posts, comments): ").strip()
            if kind not in TYPES:
                raise NetworkError("Выбери тип записи из списка")
            if choice == "2":
                for item in service.list_records(kind):
                    print(vars(item))
                continue
            if choice == "4":
                service.delete_record(kind, int(input("ID: ")))
                print("Запись удалена")
            else:
                item_id = int(input("ID: ")) if choice == "3" else None
                if item_id is not None:
                    service.get_record(kind, item_id)
                values = {key: input(f"{key}: ") for key in TYPES[kind][1]}
                item = service.write_record(kind, values, item_id)
                print(f"Сохранено, ID: {item.id}")
        except (
            NetworkError, ValueError, OSError, KeyError, TypeError
        ) as error:
            print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            return
