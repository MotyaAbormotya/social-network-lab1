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


def find(rows: dict[int, Record], item_id: int) -> Record:
    if item_id not in rows:
        raise NetworkError(f"Запись с ID {item_id} не найдена")
    return rows[item_id]


def store(rows: dict[int, Record], item: Record):
    rows[item.id] = item


def make_record(data: Data, kind: str, values: dict[str, object]) -> Record:
    constructor, columns = TYPES[kind]
    parsed: dict[str, str | int] = {}
    for field in ("id", *columns):
        value = values[field]
        if field == "id" or field.endswith("_id"):
            if type(value) not in (int, str) or int(value) < 1:
                raise NetworkError(f"{field} должен быть положительным числом")
            parsed[field] = int(value)
        elif isinstance(value, str) and value.strip():
            parsed[field] = value
        else:
            raise NetworkError(f"Поле {field} не должно быть пустым")
    if "author_id" in parsed:
        find(data["users"], int(parsed["author_id"]))
    if "post_id" in parsed:
        find(data["posts"], int(parsed["post_id"]))
    return constructor(**parsed)


def delete_record(data: Data, kind: str, item_id: int):
    field = {"users": "author_id", "posts": "post_id"}.get(kind)
    for group in data.values():
        if field and any(
            getattr(item, field, None) == item_id for item in group.values()
        ):
            raise NetworkError("На эту запись ссылаются другие записи")
    del data[kind][item_id]


def main():
    data: Data = {kind: {} for kind in TYPES}
    while True:
        try:
            print("\n1. Создать  2. Список  3. Изменить  4. Удалить  0. Выход")
            choice = input("Действие: ").strip()
            if choice == "0":
                break
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
                find(rows, item_id)
            if choice == "4":
                delete_record(data, kind, item_id)
                print("Запись удалена")
            else:
                columns = TYPES[kind][1]
                values = {field: input(f"{field}: ") for field in columns}
                item = make_record(data, kind, {"id": item_id, **values})
                store(rows, item)
                print(f"Сохранено, ID: {item_id}")
        except (NetworkError, ValueError) as error:
            print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()
