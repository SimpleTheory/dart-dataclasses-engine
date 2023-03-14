import dataclasses as dc
import dart_dataclasses.domain as domain
from pathlib import Path
import re
import dart_dataclasses.parsing.config_file as conf
import dart_dataclasses.writing.class_functions as cf

# TODO ADD IMPORTS TO PAGE

@dc.dataclass
class Tag:
    tag: str
    associated_class: domain.Class
    start: int
    end: int = None
    str_to_replace: str = None

    @classmethod
    def create(cls, tag: re.Match, associated_class: domain.Class, file_content):
        if tag == '@Generate':
            return cls(tag.group(), associated_class, tag.start(), tag.end())
        start = tag.start()
        clipped = file_content[start:]
        end = re.search('// </Dataclass>', clipped).end()
        return cls(tag.group(), associated_class, start, end, file_content[start:end + 1])

    def replace(self, file_content: str):
        return file_content[:self.start] + \
            write_class_functions_main(self.associated_class) + \
            file_content[self.end + 1:]


def dir_level_insertions(file_dataclasses: dict[Path: dict[str:list[domain.Class] | list[domain.Enum]]]):
    for file, file_objects in file_dataclasses.items():
        dataclasses = file_objects['dataclasses']
        if dataclasses:
            dataclass_insertions(file, dataclasses)


def dataclass_insertions(file: Path, dataclasses: list[domain.Class]):
    with open(file, 'r') as f:
        file_content = f.read()
    new_file_content = get_and_replace_tags(file_content, dataclasses)
    print(new_file_content)
    # with open(file, 'w') as f: TODO UNCOMMENT
    #     f.write(new_file_content)

def get_class_ranges(dataclasses: list[domain.Class], file_content: str) -> dict[domain.Class: int]:
    return {class_: re.search(f'\sclass\s+{class_.name}', file_content).span()[0] for class_ in dataclasses}


def get_and_replace_tags(file_content: str, dataclasses):
    class_ranges = get_class_ranges(dataclasses, file_content)
    mark = re.search('@Generate|// <Dataclass>', file_content)
    while mark:
        current = Tag.create(mark, find_associated_class(mark, class_ranges), file_content)
        file_content = current.replace(file_content)
        mark = re.search('@Generate|// <Dataclass>', file_content)
    return file_content


def find_associated_class(tag, class_ranges):
    iterator = list(class_ranges.items())
    for index, class__pos in iterator:
        try:
            next_pos = iterator[index + 1][1]
            if class__pos[1] < tag.start < next_pos:
                return class__pos[0]
        except IndexError:
            return class__pos[0]


def write_class_functions_main(dart_class: domain.Class) -> str:
    return cf.left_pad_string(
        conf.encapsulate_region(name='Dataclass Section',
                                text=f'''
// <Dataclass>
{conf.warning_message}

{cf.class_functions(dart_class)}
// </Dataclass>
    '''.lstrip()), 2)
