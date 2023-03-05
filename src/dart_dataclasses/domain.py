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
        import dart_dataclasses.parsing.file_content_cleaning as cc
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
        # Clean
        generics_string = generics_string.strip()
        generics_string = generics_string[1:] if generics_string.startswith('<') else generics_string
        generics_string = generics_string[:-1] if generics_string.endswith('>') else generics_string
        # Sub
        generics_string, saved_sub_generics = Type.clean_generics_in_generics_string(generics_string)
        # Parse
        generics = [Type.reinsert_subgeneric(i.strip(), saved_sub_generics) for i in generics_string.split(',')]
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

    @staticmethod
    def clean_generics_in_generics_string(generics_string: str) -> tuple[str, list[str]]:
        bracket_cnt = 0
        sub_generics = []
        starts = []
        ends = []
        for index, char in enumerate(generics_string):
            if char == '<':
                if not bracket_cnt:
                    starts.append(index)
                bracket_cnt += 1
            if char == '>':
                bracket_cnt -= 1
                if not bracket_cnt:
                    ends.append(index)
        for start, end in zip(starts, ends):
            sub_generics.append(generics_string[start:end+1])
        for index, sub_generic in enumerate(sub_generics):
            generics_string = generics_string.replace(sub_generic, f'____sub_{index}____', 1)
        return generics_string, sub_generics

    @staticmethod
    def reinsert_subgeneric(str_to_sub: str, saved_subs: list[str]) -> str:
        match = re.search('____sub_(\d+)____', str_to_sub)
        while match:
            str_to_sub = str_to_sub.replace(match.group(0), saved_subs[int(match.group(1))])
            match = re.search('____sub_(\d+)____', str_to_sub)
        return str_to_sub

    def to_str(self):
        result = self.type
        generics = ''
        if self.generics:
            generics = f'<{", ".join([t.to_str() for t in self.generics])}>'
        null = '?' if self.nullable else ''
        return result + generics + null


@dataclass()
class Attribute:
    name: str
    type: Type
    final: bool
    static: bool
    const: bool
    late: bool
    external: bool
    default_value: str | None
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
iterable_types = [
    'List',
    'Map',
    'Set',
    'Iterable',
    'HashMap',
    'LinkedHashSet',
    'LinkedHashMap',
    'Queue',
    'ListQueue',
    'SplayTreeSet',
    'SplayTreeMap'
]
# reset_iterable_types
