import re
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps


class MethodType(Enum):
    normal = 1
    constructor = 2
    factory = 3
    named_constructor = 4
    setter = 5
    operator = 6


def to_dart_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            result = result.replace('True', 'true') \
                .replace('False', 'false') \
                .replace('None', 'null') \
                .replace('MethodType.named_constructor', 'MethodType.namedConstructor')
        return result

    return wrapper


def list_to_string(list_: list, extra_lines=True, padding: int = 6):
    if extra_lines:
        newline = '\n' + (' ' * padding)
        return f'[{newline}{f", {newline}".join(list_)}\n{" " * (padding - 2)}]'
    return f'[{", ".join(list_)}]'


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
                    break
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

    @to_dart_wrapper
    def to_dart(self):
        return f'Annotation.create(\'{self.name}\', {list_to_string(self.positional_params, False)}, {self.keyword_params})'


@dataclass()
class DartEnum:
    name: str
    options: list[str]


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
            sub_generics.append(generics_string[start:end + 1])
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

    @to_dart_wrapper
    def to_dart(self):
        return f'ReflectedType.create({self.type if self.type != "void" else "null"},' \
               f' \'{self.to_str()}\')'


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

    @to_dart_wrapper
    # TODO FIX THIS ADD CONFIG OPTION AND PROPER DEFAULTS
    def to_dart(self, associated_class: 'Class' = None):
        if not self.default_value:
            default_value = 'null'
        elif all([associated_class, self.static, not self.private]):
            default_value = f'{associated_class.name}.{self.name}'
        else:
            default_value = f'\'{self.default_value}\''
        super_param = f", \'{self.super_param}\'" if self.super_param else ''

        return f'Attribute.create(\'{self.name}\', {self.type.to_dart()}, {self.final}, {self.static}, {self.const},' \
               f' {self.late}, {self.external}, {default_value}{super_param})'


@dataclass()
class Getter:
    return_type: Type
    name: str
    external: bool
    static: bool
    private: bool = field(init=False)
    referenced_private_variable: Attribute = None

    def __post_init__(self):
        self.private = self.name.startswith('_')
        self.name = self.name[:-1] if self.name.endswith(';') else self.name

    @to_dart_wrapper
    def to_dart(self, associated_class: 'Class' = None):
        reference = ''
        if associated_class and self.static:
            reference = f', {associated_class.name}.{self.name}'
        return f'Getter.create({self.return_type.to_dart()}, \'{self.name}\',' \
               f' {self.external}, {self.static}{reference})'


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

    @to_dart_wrapper
    def to_dart(self, associated_class: 'Class' = None):
        from dart_dataclasses.parsing.config_file import reference_private_methods
        reference = 'null'
        generics = f"\'{self.generics}\'" if self.generics else "null"
        if all([associated_class, (not self.private or reference_private_methods),
                any([
                    self.method_type == MethodType.factory,
                    self.static,
                    self.method_type == MethodType.named_constructor])]):
            reference = f"{associated_class.name}.{self.name}"
        return f'Method.create(\'{self.name}\', {self.return_type.to_dart()}, {self.method_type},' \
               f' {self.static}, {generics}, {self.external}, {reference})'


@dataclass()
class Class:
    name: str
    dataclass_annotation: Annotation
    attributes: list[Attribute]  # = field(default_factory=list)
    methods: list[Method]  # = field(default_factory=list)
    getters: list[Getter]  # = field(default_factory=list)
    parent: str = None

    # mixin: list[str] = None
    # implements: list[str] = None

    def to_dart(self, padding=2):
        result = f'''ReflectedClass(
    name: '{self.name}',
    referenceType: {Type(self.name, False).to_dart()},
    dataclassAnnotation: {self.dataclass_annotation.to_dart()},
    attributes: {list_to_string([attr.to_dart(self) for attr in self.attributes])},
    getters: {list_to_string([gettr.to_dart(self) for gettr in self.getters])},
    methods: {list_to_string([method.to_dart(self) for method in self.methods], True)},
    parent: {self.parent if self.parent else "null"}
  )
            
        '''.strip()

        return result


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
