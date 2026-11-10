from pathlib import Path

from domain.models import Data, NetworkError, Record, TYPES
from domain.repository import NetworkRepository


def make_record(data: Data, kind: str, values: dict[str, object]) -> Record:
    parsed: dict[str, str | int] = {}
    constructor, columns = TYPES[kind]
    for field in ("id", *columns):
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
    return constructor(**parsed)


class NetworkService:
    def __init__(self, repository: NetworkRepository):
        self.repository = repository
        self.data: Data = {kind: {} for kind in TYPES}

    def list_records(self, kind: str) -> list[Record]:
        return list(self.data[kind].values())

    def get_record(self, kind: str, item_id: int) -> Record:
        rows = self.data[kind]
        if item_id not in rows:
            raise NetworkError(f"Запись с ID {item_id} не найдена")
        return rows[item_id]

    def write_record(
        self, kind: str, values: dict[str, object], item_id: int | None = None
    ) -> Record:
        rows = self.data[kind]
        if item_id is None:
            item_id = max(rows, default=0) + 1
        else:
            self.get_record(kind, item_id)
        item = make_record(self.data, kind, {**values, "id": item_id})
        rows[item_id] = item
        return item

    def delete_record(self, kind: str, item_id: int):
        self.get_record(kind, item_id)
        field = {"users": "author_id", "posts": "post_id"}.get(kind, "")
        related = [
            *self.data["posts"].values(), *self.data["comments"].values()
        ]
        if any(getattr(item, field, None) == item_id for item in related):
            raise NetworkError("На эту запись ссылаются другие записи")
        del self.data[kind][item_id]

    def load(self, path: Path):
        groups = self.repository.read(path)
        data: Data = {kind: {} for kind in TYPES}
        for kind, rows in data.items():
            records = groups[kind]
            if not isinstance(records, list):
                raise NetworkError(f"В {kind} ожидается список записей")
            for values in records:
                item = make_record(data, kind, values)
                if item.id in rows:
                    raise NetworkError(f"Повторяющийся ID {item.id} в {kind}")
                rows[item.id] = item
        self.data = data

    def save(self, path: Path):
        self.repository.write(path, self.data)
