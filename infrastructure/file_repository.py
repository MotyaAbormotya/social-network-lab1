import json
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from domain.models import Data, NetworkError, TYPES


def file_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in (".json", ".xml"):
        raise NetworkError("Укажи расширение .json или .xml")
    return suffix


def parse_xml(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as error:
        raise NetworkError(f"Некорректный XML: {error}") from error


class FileRepository:
    def read(self, path: Path) -> dict[str, object]:
        if file_format(path) == ".json":
            groups = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(groups, dict):
                raise NetworkError("В JSON ожидаются группы записей")
            return groups
        root = parse_xml(path)
        if root.tag != "social_network" or any(len(row) for row in root):
            raise NetworkError("Неверная структура XML")
        groups = {kind: [] for kind in TYPES}
        for row in root:
            groups[row.tag + "s"].append(row.attrib)
        return groups

    def write(self, path: Path, data: Data):
        suffix = file_format(path)
        with TemporaryDirectory(dir=path.parent) as folder:
            temp = Path(folder) / path.name
            if suffix == ".json":
                groups = {}
                for kind, rows in data.items():
                    groups[kind] = [vars(row) for row in rows.values()]
                text = json.dumps(groups, ensure_ascii=False, indent=2)
                temp.write_text(text + "\n", encoding="utf-8", newline="\n")
            else:
                root = ET.Element("social_network")
                for kind, rows in data.items():
                    for row in rows.values():
                        values = {
                            key: str(value) for key, value in vars(row).items()
                        }
                        ET.SubElement(root, kind[:-1], values)
                ET.indent(root)
                temp.write_bytes(ET.tostring(root, encoding="utf-8") + b"\n")
                parse_xml(temp)
            temp.replace(path)
