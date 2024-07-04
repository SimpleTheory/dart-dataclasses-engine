import re
import dart_dataclasses.domain as domain
import dart_dataclasses.parsing.file_content_cleaning as cc
import dart_dataclasses.parsing.parser as par
from pathlib import Path

from dart_dataclasses.utils import project_root


def file_reading(file: Path | str, typedefs: dict[str:str] = None) -> dict[str:list[domain.Class] | list[domain.Enum]] | None:
    file = Path(file)
    if file.suffix != '.dart':
        return
    file_content, strings = cc.clean_file(file)
    if typedefs:
        file_content = cc.replace_typedefs(file_content, typedefs)
    dataclasses = file_reading_procedure_for_classes(file_content, strings)
    # if dataclasses is None:
    #     return
    enums = file_reading_procedure_for_enums(file_content)
    if dataclasses is None and enums is None:
        return
    return {
        'dataclasses': dataclasses,
        'enums': enums,
        # 'typedefs': typedefs
    }


def file_reading_for_type_defs(file: Path | str) -> dict[str: str] | None:
    """
    This only supports function style typedefs like
        typedef MyJson = Map<String,Map<String,List<List<num>>>>;
        typedef BoolFunctionMap = bool Function(MapEntry);
    """
    file = Path(file)
    if file.suffix != '.dart':
        return
    file, strings = cc.clean_file(file)
    if 'typedef' not in file:
        return dict()
    typedefs = re.findall(r'typedef\s+([a-zA-Z0-9,><\s]+?)\s*=\s*([a-zA-Z0-9,><(){}.\s]+?);', file)
    return {typedef[0]: typedef[1] for typedef in typedefs}


def file_reading_procedure_for_classes(file_content: str, strings: dict[str:list[str]]) -> \
        list[domain.Class] | None:
    if '@Dataclass' not in file_content:
        return
    pre_parsed_classes = cc.get_class_isolates(file_content)
    classes = [par.class_isolate_parsing_main(class_isolate, strings) for class_isolate in pre_parsed_classes]
    return [dataclass for dataclass in classes if dataclass.dataclass_annotation.name == 'Dataclass']


def file_reading_procedure_for_enums(file_content: str) -> list[domain.DartEnum] | None:
    if not re.search(r'\s*enum\s+', file_content):
        return
    pre_parsed_enums = cc.get_enums(file_content)
    enums = [par.parse_enum(*enum_iso) for enum_iso in pre_parsed_enums]
    return enums


def dir_procedure(dir: str | Path) -> dict[Path: dict[str:list[domain.Class] | list[domain.Enum]] | None]:
    typedefs = {}
    for file in Path(dir).glob('**/*.dart'):
        typedefs = typedefs | file_reading_for_type_defs(file)
    return {Path(file): file_reading(file, typedefs) for file in Path(dir).glob('**/*.dart')}


if __name__ == '__main__':
    a = project_root() / r'tests\test_cache\class.dart'
    a2 = project_root() / r'tests\test_cache\trying_things_out_ari_utils_2-27-2023.dart'
    b = file_reading(a)
    c = file_reading_for_type_defs(a)
    print(c)
    print()
    # c = file_reading_procedure_for_enums(a)
    b2 = file_reading(a2)
    # c2 = file_reading_procedure_for_enums(a2)