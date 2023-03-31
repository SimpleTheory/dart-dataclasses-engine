import re
import dart_dataclasses.domain as domain
import dart_dataclasses.parsing.file_content_cleaning as cc
import dart_dataclasses.parsing.parser as par
from pathlib import Path

def file_reading(file: Path | str) -> dict[str:list[domain.Class] | list[domain.Enum]] | None:
    file = Path(file)
    if file.suffix != '.dart':
        return
    file_content, strings = cc.clean_file(file)
    dataclasses = file_reading_procedure_for_classes(file_content, strings)
    if dataclasses is None:
        return
    enums = file_reading_procedure_for_enums(file_content)
    return {
        'dataclasses': dataclasses,
        'enums': enums,
    }


def file_reading_procedure_for_classes(file_content: str, strings: dict[str:list[str]]) -> \
        list[domain.Class] | None:
    if '@Dataclass' not in file_content:
        return
    pre_parsed_classes = cc.get_class_isolates(file_content)
    classes = [par.class_isolate_parsing_main(class_isolate, strings) for class_isolate in pre_parsed_classes]
    return [dataclass for dataclass in classes if dataclass.dataclass_annotation.name == 'Dataclass']
def file_reading_procedure_for_enums(file_content: str) -> list[domain.DartEnum] | None:
    if not re.search('\s*enum\s+', file_content):
        return
    pre_parsed_enums = cc.get_enums(file_content)
    enums = [par.parse_enum(*enum_iso) for enum_iso in pre_parsed_enums]
    return enums

def dir_procedure(dir: str | Path) -> dict[Path: dict[str:list[domain.Class] | list[domain.Enum]] | None]:
    return {Path(file): file_reading(file) for file in Path(dir).glob('**/*.dart')}


if __name__ == '__main__':
    a = r'D:\PycharmProjects\dart_dataclasses\tests\test_cache\class.dart'
    a2 = r'D:\PycharmProjects\dart_dataclasses\tests\test_cache\trying_things_out_ari_utils_2-27-2023.dart'
    b = file_reading(a)
    # c = file_reading_procedure_for_enums(a)
    b2 = file_reading(a2)
    # c2 = file_reading_procedure_for_enums(a2)
    pass