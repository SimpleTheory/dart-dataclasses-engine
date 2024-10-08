import re
import dart_dataclasses.domain as domain
import dart_dataclasses.parsing.file_content_cleaning as cc
from dart_dataclasses.utils import find_and_replace

type_regex = r'(\w+\s*(\<(?:[^<>]+|\<(?:[^<>]+|\<[^<>]*\>)*\>)*\>)?\??)'


def class_isolate_parsing_main(class_isolate, stored_strings):
    name, parent, dataclass_annotation, mixins, implementations = get_name(class_isolate[0], stored_strings)
    getters, attr, methods = retun_body_ast(class_isolate[1], name, stored_strings)
    return domain.Class(
        name=name,
        dataclass_annotation=dataclass_annotation,
        attributes=attr,
        methods=methods,
        getters=getters,
        parent=parent,
        mixins=mixins,
        implementations=implementations
    )


def separate_annotations(part: str, stored_strings: dict[str:str] = None) -> tuple[str, list[domain.Annotation]]:
    """
    :param stored_strings:
    :param part: Section of body to scan for annotations.
    :return: Cleaned body and Annotations related to body [annotation, args].
    """
    annotation_regex = re.compile(r'@(\w+)(\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))?')
    annotation_list: list[tuple[str, str]] = annotation_regex.findall(part)
    cleaned_part = annotation_regex.sub('', part)
    if stored_strings:
        annotations = [a.restore_strings(stored_strings) for a in
                       turn_annotation_strs_to_annotation_list(annotation_list)]
        return cleaned_part.strip(), annotations
    return cleaned_part.strip(), turn_annotation_strs_to_annotation_list(annotation_list)


def turn_annotation_strs_to_annotation_list(annotations: list[tuple[str, str]]) -> list[domain.Annotation]:
    if not annotations:
        return []
    return [domain.Annotation.from_annotation_tuple(a) for a in annotations]


def get_name(name_part: str, stored_strings: dict[str:str]) -> \
        tuple[str, str | None, domain.Annotation, list[str] | None, list[str] | None]:
    name_part, annotations = separate_annotations(name_part, stored_strings=stored_strings)
    dataclass_annotation = annotations[0]
    name = re.search(r'class\s+(\w+)', name_part).group(1)
    # Potentially Make work with something like Hi extends Bloc<InitSettingsEvent, InitSettingsState>
    parent = re.search(r'extends\s+([\w]+)', name_part).group(1) if 'extends' in name_part else None
    return name, parent, dataclass_annotation, \
        get_mixin_or_implements(name_part, 'with'), get_mixin_or_implements(name_part, 'implements')


def get_mixin_or_implements(name_part: str, get_type: str) -> list[str] | None:
    # regex_string = r'with\s+\w+\s*(\,\s*\w+\s*)*(?={|extends|implements)'
    keywords = ['with', 'extends', 'implements']
    keywords.remove(get_type)
    keywords_string = '|'.join(keywords)
    # Potentially Make work with something like Hi extends Bloc<InitSettingsEvent, InitSettingsState>
    regex = re.compile(r'(?<=get_type)\s+[\w]+\s*(\,\s*[\w]+\s*)*(?={|keywords_string)'
                       .replace('get_type', get_type)
                       .replace('keywords_string', keywords_string))
    match = regex.search(name_part)
    if not match:
        return match
    return [i.strip() for i in match.group().split(',')]


def retun_body_ast(class_body: str, class_name: str, stored_strings: str):
    class_body, named_constructors = get_and_kill_named_constructors(class_body, class_name)
    bodyparts = cc.body_seperator(class_body)
    ast = [syntax_main(bp, class_name, stored_strings) for bp in bodyparts]
    getter = []
    attr = []
    methods = [*named_constructors]
    for part in ast:
        if isinstance(part, domain.Getter):
            getter.append(part)
        elif isinstance(part, domain.Method):
            methods.append(part)
        elif isinstance(part, domain.Attribute):
            attr.append(part)
    return getter, attr, methods

def get_and_kill_named_constructors(class_body: str, class_name: str):
    regex = re.compile(r'CLS\.(\w+)\s*(\<(?:[^<>]+|\<(?:[^<>]+|\<[^<>]*\>)*\>)*\>)?\s*\(([^;]*?)\)\s*(:.+?;)'.replace('CLS', class_name), flags=re.MULTILINE | re.DOTALL)
    class_body, named_constructors = find_and_replace(regex, '', class_body)
    return class_body, [parse_shortened_named_constructor(named_con, class_name) for named_con in named_constructors]


def syntax_main(syntax_isolate: str, classname: str, stored_strings: dict[str:str], *args):
    syntax, annotations = separate_annotations(syntax_isolate,
                                               stored_strings=stored_strings)  # 1. str | 2. list[tuple[str, str]]
    syntax, keywords = preparse(syntax)
    if is_method(syntax):
        method_type = get_method_type(syntax.strip(), keywords, classname)
        return parse_method(syntax, keywords, method_type, classname, stored_strings, annotations)
    else:
        return getter_or_attr(syntax, annotations, keywords, stored_strings)


# Be on the lookout for errors caused by this function for not grabbing enough words or for wierd things
def preparse(syntax: str, return_list: list[str] = None) -> tuple[str, list[str] | None]:
    pre_word_regex = re.compile(r'(static|const|final|factory|set|external|late)\s+')  # Add more preparse words here
    syntax_characteristics = [] if return_list is None else return_list
    pre_word = pre_word_regex.match(syntax)
    if pre_word:
        cleaned_syntax = pre_word_regex.sub('', syntax, count=1)
        syntax_characteristics.append(pre_word.group(1))
        return preparse(cleaned_syntax, syntax_characteristics)
    else:
        return syntax, syntax_characteristics


def get_method_type(cleaned_method: str, keywords, classname) -> domain.MethodType:
    named_constructor_regex = re.compile(fr'{classname}\.\w+')
    operator_regex = re.compile(fr'{type_regex}\s+operator')
    regular_constructor_regex = re.compile(fr'^{classname}\s*\(')
    if 'factory' in keywords:
        return domain.MethodType.factory
    elif 'set' in keywords:
        return domain.MethodType.setter
    elif named_constructor_regex.match(cleaned_method):
        return domain.MethodType.named_constructor
    elif operator_regex.match(cleaned_method):
        return domain.MethodType.operator
    elif regular_constructor_regex.match(cleaned_method):
        return domain.MethodType.constructor
    else:
        return domain.MethodType.normal


def is_method(syntax: str) -> bool:
    r"""
    if there exists '(' before '=' or '{' it is a method else attribute
    -------------
    methods:
        name.something() {}? --named constructor
        name() --constructor
        factory
        static
        set
        \S+\s+operator
        (if not above) normal method

    attrs:
        \S+\s+get
            (separate get parser)
        ----
        if start with static||final||const:
            remove set thing to true check again
        else
            move to regular attribute work
        if has = sign
            (stripped)=(split 1st eq)default_value(delete);

        parse and apply annotations
        parse base attr
        instantiate attr obj

    :return: identifies what a bodypart is and calls the appropriate function:

    """
    previous = ''
    for char in syntax:
        if char == '(':
            return True
        elif char == '{' or (char == '>' and previous == '='):
            return False
        previous = char
    return False


def identify_getter(cleaned_attr) -> bool:
    if 'get' in cleaned_attr and re.search(r'=>|\{', cleaned_attr):
        getter_metadata = re.split(r'=>|\{', cleaned_attr)[0]
        return bool(re.search(r'\s+get\s+', getter_metadata))
    return False

def getter_or_attr(cleaned_attr, annotations, keywords, stored_strings) -> domain.Getter | domain.Attribute:
    if identify_getter(cleaned_attr):
        return parse_getter(cleaned_attr, annotations, keywords)
    return parse_attr(cleaned_attr, annotations, keywords, stored_strings)
    # return Getter with type and name

# Depreciated
def get_type_and_name_from_a_split(unpackable) -> tuple[domain.Type, str]:
    type_, name = unpackable
    return domain.Type.from_isolated_string(type_), name.strip()

# Use and implement below
def get_type_and_name_from_regex(type_name_iso_str: str, with_split: str = None) -> tuple[domain.Type, str]:
    if with_split:
        split = type_name_iso_str.split(with_split)
        type_name_iso_str = ' '.join(split)
    try:
        type_, name = [i[0].strip() for i in re.findall(type_regex, type_name_iso_str)]
    except ValueError:
        name = type_name_iso_str
        type_ = 'dynamic'
    return domain.Type.from_isolated_string(type_), name.strip()


def parse_getter(getter: str, annotations: list[str], keywords: list[str]) -> domain.Getter:
    getter_metadata = re.split(r'=>|\{', getter)[0]
    type_, name = get_type_and_name_from_a_split(re.split(r'get\s+', getter_metadata))
    # name = name.strip()
    # type_ = domain.Type.from_isolated_string(type_)
    return domain.Getter(name=name,
                         return_type=type_,
                         external='external' in keywords,
                         static='static' in keywords)


def retrieve_from_annotation_list(thing_to_retrieve: str,
                                  annotations: list[domain.Annotation]) -> domain.Annotation | None:
    """

    :param thing_to_retrieve:
    :param annotations:
    :return: Annotation as [0] = annotation name, [1] = args
    """
    for a in annotations:
        if not a:
            continue
        if a.name.lower() == thing_to_retrieve.lower():
            return a
    return None


def parse_attr(attr: str, annotations: list[domain.Annotation],
               keywords: list[str], stored_strings: dict[str:str]) -> domain.Attribute:
    """
    ---
    :param attr:
    :param annotations:
    :param keywords:
    :param stored_strings:
    :return:
    """
    attr = attr.replace(';', '')
    if '=' in attr:
        attr, default_value = attr.split('=')
        attr = attr.strip()
        default_value = cc.restore_strings(default_value.strip(), stored_strings)
    else:
        attr = attr.strip()
        default_value = None
    is_super = retrieve_from_annotation_list('Super', annotations)
    if is_super:
        try:
            super_ = is_super.positional_params[0]
        except IndexError:
            super_ = None
    else:
        super_ = None
    # Here should only be: type name
    # which is f'{type_regex}\s+(\w+)'
    type_, name = get_type_and_name_from_regex(attr)
    return domain.Attribute(
        name=name,
        type=type_,
        final='final' in keywords,
        static='static' in keywords,
        external='external' in keywords,
        const='const' in keywords,
        late='late' in keywords,
        default_value=default_value,
        super_param=super_
    )


def cut_method_body(method: str) -> tuple[str, str]:
    result: list[str] = (method.rsplit(')', 1)[0] + ')').split('(', 1)
    result[1] = '(' + result[1]
    result = [t.strip() for t in result]
    return tuple(result)


def parse_method(method: str, keywords: list[str], method_type: domain.MethodType, classname: str,
                 stored_strings: dict[str:str], annotations: list[domain.Annotation] = None):
    """
    Parse methods
    -----
    (close after last ')')
    Class.method()
    Class()
    type operator method()
    type method() (normal, set, factory)
    --------
    name: str ~{{
    return_type: Type ~{{

    method_type: MethodType ~
    static: bool ke
    generics: bool ~
    external: bool ke
    parameters_string ~
    """
    # Establish return_type, name,
    method, method_args = cut_method_body(method)
    if method_type == domain.MethodType.operator:
        type_, name = get_type_and_name_from_a_split([i.strip() for i in method.split('operator')])
    generics_match = re.search('(<(?:[^<>]+|<(?:[^<>]+|<[^<>]*>)*>)*>)$', method)
    generics = None
    if generics_match:
        generics = generics_match.group()
        method = method.replace(generics, '').strip()
    # External Default Constructor Clause
    if all(['external' in keywords, 'factory' in keywords, method == classname]):
        method_type = domain.MethodType.constructor
    if method_type == domain.MethodType.named_constructor or method_type == domain.MethodType.factory:
        try:
            type_ = classname
            name = method.split('.')[1]
        except IndexError:
            type_ = classname
            name = 'returnsSingletonObject'
            method_type = domain.MethodType.constructor

    elif method_type == domain.MethodType.constructor:
        type_ = classname
        name = classname
    elif method_type == domain.MethodType.operator:
        pass
    elif method_type == domain.MethodType.setter:
        type_ = domain.Type('void', False)
        name = method
    else:
        x = re.search(fr'{type_regex}\s+(\w+)', method)
        # type_ = x.group(1) + x.group(2) if x.group(2) else x.group(1)
        type_ = x.group(1) if x else 'dynamic'
        # print(type_)
        name = x.group(3) if x else method

    return domain.Method(
        name=name,
        return_type=type_ if isinstance(type_, domain.Type) else domain.Type.from_isolated_string(type_),
        method_type=method_type,
        static='static' in keywords,
        generics=generics,
        external='external' in keywords,
        parameters_string=method_args,
    )


def parse_shortened_named_constructor(match: re.Match, class_name):
    return domain.Method(
        name=match.group(1),
        return_type=domain.Type.from_isolated_string(class_name),
        method_type=domain.MethodType.named_constructor,
        static=False,
        generics=match.group(2),
        external=False,
        parameters_string='()' if not match.group(3) else match.group(3),
    )

def parse_enum(name: str, enum_iso: str) -> domain.DartEnum:
    return domain.DartEnum(name, split_enum_body_and_get_options(enum_iso.strip()[:-1].strip()))


def split_enum_body_and_get_options(body: str) -> list[str]:
    body = body.strip()
    split = body.split(';', maxsplit=1)
    enum_options = split[0]
    return parse_enum_options(enum_options)
    # if len(split) == 2:
    #     enum_options = split[0]
    # else:
    #     enum_options = s
    # return [i.strip() for i in re.split(r'[,;]', body) if i]


def parse_enum_options(enum_options: str) -> list[str]:
    enum_options = enum_options[1:].strip() if enum_options.startswith('{') else enum_options.strip()
    enum_options = re.sub(r'(\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))', '', enum_options)  # gets rid of nested ()
    enum_options_list = [i.strip() for i in enum_options.split(',')]
    result = []
    for option in enum_options_list:
        # print('-------')
        # print(option)
        if '(' in option:
            # print(option[0])
            result.append(option.split('(')[0].strip())
        elif not option.strip():
            continue
        else:
            result.append(option.strip())
    return result


"""
Things to parse
In name:
    dataclass parameters
    class name
    parent name
    
In class body:
    default constructor
    methods (of all types):
        setters
        factory
        named constructor
        
    getters
    attributes (of all types):
        
"""

if __name__ == '__main__':
    test = '''@override
@deprieciated
@super(+)
@default([hi(b()), w()])
list<int> bro;
    '''
    x = separate_annotations(test)
    print(x)
    y = 'class NamedPet extends Pet with Named, thing implements words{'
    print(get_mixin_or_implements(y, 'with'))
    print(get_mixin_or_implements(y, 'implements'))
