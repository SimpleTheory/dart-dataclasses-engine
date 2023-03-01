import re
import dart_dataclasses.domain as domain
import dart_dataclasses.parsing.file_content_cleaning as cc
import dart_dataclasses.parsing.parser as par
from pathlib import Path


def file_reading_procedure_for_classes(file: Path | str) -> list[domain.Class] | None:
    if not str(file).endswith('.dart'):
        return
    file_content, strings = cc.clean_file(file)
    if '@Dataclass' not in file_content:
        return
    pre_parsed_classes = cc.get_class_isolates(file_content)
    classes = [par.class_isolate_parsing_main(class_isolate, strings) for class_isolate in pre_parsed_classes]
    return classes

def file_reading_procedure_for_enums(file: Path | str) -> list[domain.DartEnum] | None:
    if not str(file).endswith('.dart'):
        return
    file_content, strings = cc.clean_file(file)
    if not re.search('\s*enum\s+', file_content):
        return
    pre_parsed_enums = cc.get_enums(file_content)
    enums = [par.parse_enum(*enum_iso) for enum_iso in pre_parsed_enums]
    return enums

def dir_procedure(dir: str | Path):
    dir = Path(dir)
    file_classes = {file: file_reading_procedure_for_classes(file) for file in dir.glob('*/**.dart')}
    file_classes = {k: v for k, v in file_classes.items() if v}
    file_enums = {file: file_reading_procedure_for_enums(file) for file in dir.glob('*/**.dart')}
    file_enums = {k: v for k, v in file_enums.items() if v}
    return file_classes, file_enums


if __name__ == '__main__':
    a = r'D:\PycharmProjects\dart_dataclasses\test\test_cache\class.dart'
    a2 = r'D:\StudioProjects\ari_utils\test\trying_things.dart'
    b = file_reading_procedure_for_classes(a)
    c = file_reading_procedure_for_enums(a)
    b2 = file_reading_procedure_for_classes(a2)
    c2 = file_reading_procedure_for_enums(a2)
    pass