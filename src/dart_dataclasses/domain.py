import re
from dataclasses import dataclass, field
from enum import Enum


class MethodType(Enum):
    normal = 1
    constructor = 2
    factory = 3
    named_constructor = 4
    setter = 5
    operator = 6


@dataclass()
class Annotation:
    name: str
    positional_params: list[str]
    keyword_params: dict[str:str]

    @classmethod
    def from_annotation_tuple(cls, annotation_tuple):
        args: list[str] = annotation_tuple[1][1:-1].split(',')
        if len(args) == 1 and not args[0]:
            return cls(annotation_tuple[0].strip(), [], {})
        pos = []
        kwarg = {}
        for arg in args:
            if arg.startswith('____') and arg.endswith('____'):
                pos.append(arg.strip())
                continue
            for i, char in enumerate(arg):
                if char == ':':
                    key, value = arg.split(':', 1)
                    kwarg[key.strip()] = value.strip()
                    continue
                if i == len(arg) - 1:
                    pos.append(arg)
        return cls(annotation_tuple[0], pos, kwarg)

    def restore_strings(self, stored_strings: dict[str:str]):
        import src.parsing.file_content_cleaning as cc
        for i in range(len(self.positional_params)):
            self.positional_params[i] = cc.restore_strings_while_loop(self.positional_params[i], stored_strings)
            # string = cc.stored_string_regex.search(self.positional_params[i])
            # while string:
            #     self.positional_params[i] = self.positional_params[i].replace(
            #         string.group(), cc.access_a_string(string.group(), stored_strings)[1:-1])
            #     string = cc.stored_string_regex.search(self.positional_params[i])
        for k in self.keyword_params.keys():
            self.keyword_params[k] = cc.restore_strings_while_loop(self.keyword_params[k], stored_strings)
            # string = cc.stored_string_regex.search(self.keyword_params[k])
            # while string:
            #     self.keyword_params[k] = self.keyword_params[k].replace(
            #         string.group(), cc.access_a_string(string.group(), stored_strings)[1:-1])
            #     string = cc.stored_string_regex.search(self.keyword_params[k])
        return self

@dataclass()
class DartEnum:
    name: str
    options: list[str]

# class Annotation:
#     pass
#
#
# @dataclass()
# class DataclassAnnotation(Annotation):
#     eq: bool = None
#     toJson: bool = None
#     attributes: bool = None
#     toStr: bool = None
#     copyWith: bool = None
#
#
# @dataclass()
# class SuperAnnotation(Annotation):
#     param: str
#
#     @classmethod
#     def from_part(cls, part: str, string_storage):
#         from src.parsing.file_content_cleaning import access_a_string
#         # part = (part.split(')')[0] + ')')[1:]
#         # parent = re.search(r'(?<=parent:)\s*[\<\>a-zA-Z0-9]', part).group().strip()
#         param = access_a_string(re.search(r'____\w+_\w+:\d+____', part).group(), string_storage)[1:-1]
#         return cls(param)
#
#
# @dataclass()
# class DefaultAnnotation(Annotation):
#     value: str
#
#     @classmethod
#     def from_part(cls, part: str, string_storage):
#         from src.parsing.file_content_cleaning import access_a_string
#         # part = (part.split(')')[0] + ')')[1:]
#         # parent = re.search(r'(?<=parent:)\s*[\<\>a-zA-Z0-9]', part).group().strip()
#         param = access_a_string(re.search(r'____\w+_\w+:\d+____', part).group(), string_storage)[1:-1]
#         return cls(param)


@dataclass()
class Type:
    type: str
    nullable: bool
    generics: list['Type'] = field(default_factory=list)

    @classmethod
    def from_isolated_string(cls, isolated_string: str):
        isolated_string = isolated_string.strip()
        nullable = False
        if isolated_string.endswith('?'):
            nullable = True
            isolated_string = isolated_string[:-1]
        if '<' in isolated_string:
            current, generics = isolated_string.split('<', 1)
            generics = '<' + generics
            return cls(current, nullable, Type.get_type_list(generics))
        else:
            return cls(isolated_string, nullable)

    @staticmethod
    def get_type_list(generics_string: str) -> list['Type']:
        generics_string = generics_string.strip()
        generics_string = generics_string[1:] if generics_string.startswith('<') else generics_string
        generics_string = generics_string[:-1] if generics_string.endswith('>') else generics_string
        generics = [i.strip() for i in re.split(r',(?![^<>]*>)', generics_string)]
        list_of_types = [Type.from_isolated_string(type_) for type_ in generics]
        return list_of_types
        # if '<' in type_:
        #     start=False
        #     cnt=0
        #     for i, char in enumerate(type_):
        #         if char == '<':
        #             if not start: start=True
        #             cnt+=1
        #         elif char == '>':
        #             cnt-=1
        #         if start and not cnt:


@dataclass()
class Attribute:
    name: str
    type: Type
    final: bool
    static: bool
    const: bool
    late: bool
    default_value: str
    private: bool = field(init=False)
    super_param: str = None

    def __post_init__(self):
        self.private = self.name.startswith('_')


@dataclass()
class Getter:
    return_type: Type
    name: str
    external: bool
    static: bool
    referenced_private_variable: Attribute = None


@dataclass()
class Method:
    name: str
    return_type: Type
    method_type: MethodType
    static: bool
    generics: str | None
    external: bool
    private: bool = field(init=False)
    parameters_string: str = '()'

    # parameters: list[Attribute] = field(default_factory=list)

    def __post_init__(self):
        self.private = self.name.startswith('_')


@dataclass()
class Class:
    name: str
    dataclass_annotation: Annotation
    attributes: list[Attribute]  # = field(default_factory=list)
    # has_default_constructor: bool = False
    methods: list[Method]  # = field(default_factory=list)
    # operators: list[str] = field(default_factory=list)
    getters: list[Getter]  # = field(default_factory=list)
    parent: str = None
    # generics: list['Type'] = field(default_factory=list)


json_safe_types = ['List', 'Map', 'int', 'String', 'double', 'num', 'bool']
types_with_extensions = ['DateTime', 'BigInt', 'Enum', 'Uri', 'Duration']
