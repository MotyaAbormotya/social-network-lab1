import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Post:
    def __init__(self, id: int, author_id: int, text: str):
        self.id = id
        self.author_id = author_id
        self.text = text

class Comment:
    def __init__(
        self, id: int, post_id: int, author_id: int, text: str
    ):
        self.id = id
        self.post_id = post_id
        self.author_id = author_id
        self.text = text

class NetworkError(Exception):
    pass

Record = User | Post | Comment
Data = dict[str, dict[int, Record]]
TYPES = {
    "users": (User, ("name",)),
    "posts": (Post, ("author_id", "text")),
    "comments": (Comment, ("post_id", "author_id", "text")),
}

def make_record(data: Data, kind: str, values: dict[str, object]) -> Record:
    parsed: dict[str, str | int] = {}
    for field in ("id", *TYPES[kind][1]):
        value = values[field]
        if field == "id" or field.endswith("_id"):
            value = int(str(value))
            if value < 1:
                raise NetworkError(f"{field} должен быть положительным числом")
        elif not isinstance(value, str) or not value.strip():
            raise NetworkError(f"Поле {field} не должно быть пустым")
        parsed[field] = value
    for field, group in (("author_id", "users"), ("post_id", "posts")):
        if field in parsed and int(parsed[field]) not in data[group]:
            raise NetworkError(f"Не найдена связанная запись {field}")
    return TYPES[kind][0](**parsed)

def delete_record(data: Data, kind: str, item_id: int):
    field = {"users": "author_id", "posts": "post_id"}.get(kind, "")
    related = [*data["posts"].values(), *data["comments"].values()]
    if any(getattr(item, field, None) == item_id for item in related):
        raise NetworkError("На эту запись ссылаются другие записи")
    del data[kind][item_id]

def load(path: Path) -> Data:
    if path.suffix.lower() == ".json":
        groups = json.loads(path.read_text(encoding="utf-8"))
    else:
        root = ET.parse(path).getroot()
        if root.tag != "social_network" or any(len(row) for row in root):
            raise NetworkError("Неверная структура XML")
        groups = {kind: [] for kind in TYPES}
        for row in root:
            groups[row.tag + "s"].append(row.attrib)
    data: Data = {kind: {} for kind in TYPES}
    for kind, rows in data.items():
        if not isinstance(groups[kind], list):
            raise NetworkError(f"В {kind} ожидается список записей")
        for values in groups[kind]:
            item = make_record(data, kind, values)
            if item.id in rows:
                raise NetworkError(f"Повторяющийся ID {item.id} в {kind}")
            rows[item.id] = item
    return data

def save(path: Path, data: Data):
    with TemporaryDirectory(dir=path.parent) as folder:
        temp = Path(folder) / path.name
        if path.suffix.lower() == ".json":
            groups = {}
            for kind, rows in data.items():
                groups[kind] = [vars(row) for row in rows.values()]
            text = json.dumps(groups, ensure_ascii=False, indent=2)
            temp.write_text(text + "\n", encoding="utf-8", newline="\n")
        else:
            root = ET.Element("social_network")
            for kind, rows in data.items():
                for row in rows.values():
                    values = {key: str(val) for key, val in vars(row).items()}
                    ET.SubElement(root, kind[:-1], values)
            ET.indent(root)
            temp.write_bytes(ET.tostring(root, encoding="utf-8") + b"\n")
            ET.parse(temp)
        temp.replace(path)

def main():
    data: Data = {kind: {} for kind in TYPES}
    while True:
        try:
            print("\n1. Создать  2. Список  3. Изменить  4. Удалить"
                  "\n5. Сохранить  6. Загрузить  0. Выход")
            choice = input("Действие: ").strip()
            if choice == "0":
                break
            if choice in ("5", "6"):
                path = Path(input("Путь к файлу: ").strip())
                if path.suffix.lower() not in (".json", ".xml"):
                    raise NetworkError("Укажи расширение .json или .xml")
                if choice == "5":
                    save(path, data)
                else:
                    data = load(path)
                print("Готово")
                continue
            if choice not in ("1", "2", "3", "4"):
                raise NetworkError("Выбери действие из меню")
            kind = input("Тип (users, posts, comments): ").strip()
            if kind not in TYPES:
                raise NetworkError("Выбери тип записи из списка")
            rows = data[kind]
            if choice == "2":
                for item in rows.values():
                    print(vars(item))
                continue
            item_id = max(rows, default=0) + 1
            if choice in ("3", "4"):
                item_id = int(input("ID: "))
                if item_id not in rows:
                    raise NetworkError(f"Запись с ID {item_id} не найдена")
            if choice == "4":
                delete_record(data, kind, item_id)
                print("Запись удалена")
            else:
                values = {key: input(f"{key}: ") for key in TYPES[kind][1]}
                values["id"] = item_id
                rows[item_id] = make_record(data, kind, values)
                print(f"Сохранено, ID: {item_id}")
        except (NetworkError, ValueError, OSError, ET.ParseError,
                KeyError, TypeError) as error:
            print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
