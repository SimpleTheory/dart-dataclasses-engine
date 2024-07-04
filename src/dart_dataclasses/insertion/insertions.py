import dataclasses as dc
import dart_dataclasses.domain as domain
from pathlib import Path
import re
import dart_dataclasses.parsing.config_file as conf
import dart_dataclasses.writing.class_functions as cf
import dart_dataclasses.file_level.cmd_line_level as cmd
from dart_dataclasses.writing.metadata import pop_lib_decorator


@dc.dataclass
class Tag:
    tag: str
    associated_class: domain.Class
    start: int
    type: str
    end: int = None
    str_to_replace: str = None

    def __post_init__(self):
        if not (self.end is None):
            self.end += 1

    @classmethod
    def create_for_dataclass_insertions(cls, tag: re.Match, associated_class: domain.Class, file_content):
        if tag.group() == '@Generate()':
            return cls(tag.group(), associated_class, tag.start(), 'generate', tag.end())
        start = tag.start()
        clipped = file_content[start:]
        end = re.search('// </Dataclass>', clipped).end()
        return cls(tag.group(), associated_class, start, 'replace', start + end, file_content[start:end])

    @classmethod
    def create_general(cls, tag: re.Match, associated_class: domain.Class = None):
        tag_type = tag.group().split(')')[0] + ')'
        return cls(tag.group(0), associated_class, tag.start(0),
                   tag_type, tag.end(0), tag.group(0))

    def replace(self, file_content: str, all_: list[domain.Class | domain.DartEnum]):
        return file_content[:self.start] + \
            write_class_functions_main(self.associated_class, all_, self.type == 'generate') + \
            file_content[self.end:]

    def replace_with(self, file_content: str, func: callable, *args, **kwargs):
        return file_content[:self.start] + \
            func(*args, **kwargs) + \
            file_content[self.end:]

def dir_level_insertions(file_dataclasses: dict[Path: dict[str:list[domain.Class] | list[domain.DartEnum]]]):
    for file, file_objects in file_dataclasses.items():
        if not file_objects:
            continue
        dataclasses = file_objects['dataclasses']
        all_ = comprehensive_list_of_all_dataclasses_and_enums(file_dataclasses)
        if dataclasses:
            dataclass_insertions(file, dataclasses, all_)
            insert_imports_if_not_there(file)
            if conf.format_files_with_insertion:
                cmd.format_file(file)


def dataclass_insertions(file: Path, dataclasses: list[domain.Class], dataclasses_and_enums: list[domain.Class | domain.DartEnum]):
    with open(file, 'r') as f:
        file_content = f.read()
    new_file_content = get_and_replace_tags(file_content, dataclasses, dataclasses_and_enums)
    # Untag to not be stuck in recursive loop
    new_file_content = new_file_content. \
        replace('//<Dataclass>', '// <Dataclass>'). \
        replace('//</Dataclass>', '// </Dataclass>')
    # print(new_file_content)
    with open(file, 'w') as f:
        f.write(new_file_content)

def comprehensive_list_of_all_dataclasses_and_enums(initial_file_classes: dict[Path: dict[str: list[domain.Class | domain.DartEnum] | None]]) -> list[domain.Class | domain.DartEnum]:
    result = []
    for file_dict in initial_file_classes.values():
        if file_dict:
            for class_collection in file_dict.values():
                if class_collection:
                    for class_obj in class_collection:
                        result.append(class_obj)
    return result


def get_class_ranges(dataclasses: list[domain.Class], file_content: str) -> list[tuple[domain.Class, int]]:
    # return [(class_, re.search(f'\sclass\s+{class_.name}\b', file_content).span()[0]) for class_ in dataclasses]
    result = []
    for class_ in dataclasses:
        boundary = re.search(fr'\sclass\s+{class_.name}\b', file_content)
        current = (class_, boundary.span()[0])
        result.append(current)
    return result

def get_and_replace_tags(file_content: str, dataclasses, dataclasses_and_enums: list[domain.Class | domain.DartEnum]):
    tag_regex = re.compile(r'(?<!//)@Generate\(\)\s+// <Dataclass>|(?<!//)@Generate\(\)(?!\s+//<Dataclass>)')
    class_ranges = get_class_ranges(dataclasses, file_content)
    mark = tag_regex.search(file_content)
    while mark:
        current = Tag.create_for_dataclass_insertions(mark, find_associated_class(mark, class_ranges), file_content)
        file_content = current.replace(file_content, dataclasses_and_enums)
        class_ranges = get_class_ranges(dataclasses, file_content)
        mark = tag_regex.search(file_content)
    return file_content


def find_associated_class(tag: re.Match, class_ranges: list[tuple[domain.Class, int]]):
    for index, class__pos in enumerate(class_ranges):
        try:
            next_pos = class_ranges[index + 1][1]
            if class__pos[1] < tag.start() < next_pos:
                return class__pos[0]
        except IndexError:
            return class__pos[0]


def write_class_functions_main(dart_class: domain.Class, all_: list[domain.Class | domain.DartEnum], encapsulate=True) -> str:
    if encapsulate:
        return cf.left_pad_string(
            conf.encapsulate_region(name='Dataclass Section',
                                    text=f'''
    
{conf.default_regeneration}//<Dataclass>
    
    {conf.warning_message}
    
{cf.class_functions(dart_class, all_)}
    //</Dataclass>
        '''.lstrip()), 2, False)
    return cf.left_pad_string(
        f'''
{conf.default_regeneration}//<Dataclass>
    
    {conf.warning_message}

    {cf.class_functions(dart_class, all_)}
    //</Dataclass>
        '''.lstrip(), 2, False)

@pop_lib_decorator
def get_metadata_import_str():
    self = str(conf.metadata_file.relative_to(conf.cwd.parent)).replace('\\', '/')
    return f'import \'package:{self}\';'

def insert_imports_if_not_there(path: Path):
    # import 'package:my_project/lib/my_library.dart';
    with open(path, 'r') as f:
        content = f.read()
    import_str = get_metadata_import_str()
    json_import = "import 'dart:convert';"
    # print(relation)
    # print(import_str)
    if not re.search("import [\'\"]dart:convert[\'\"];", content):
        content = f'{json_import}\n{content}'
    if import_str not in content:
        content = f'{import_str}\n{content}'
    with open(path, 'w') as f:
        f.write(content)

# if __name__ == '__main__':
#     conf.cwd = Path(r'D:\StudioProjects\test_dataclasses\lib\test_dataclasses.dart').parent.parent
#     conf.metadata_file = Path(r'D:\StudioProjects\test_dataclasses\mydataclasses\metadata.dart')
#     insert_imports_if_not_there(Path(r'D:\StudioProjects\test_dataclasses\lib\test_dataclasses.dart'))
