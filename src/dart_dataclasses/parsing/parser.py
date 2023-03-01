import re
import dart_dataclasses.domain as domain
import dart_dataclasses.parsing.file_content_cleaning as cc

type_regex = r'(\w+(\<(?:[^<>]+|\<(?:[^<>]+|\<[^<>]*\>)*\>)*\>)?)'


def class_isolate_parsing_main(class_isolate, stored_strings):
    name, parent, dataclass_annotation = get_name(class_isolate[0], stored_strings)
    getters, attr, methods = retun_body_ast(class_isolate[1], name, stored_strings)
    return domain.Class(
        name=name,
        dataclass_annotation=dataclass_annotation,
        attributes=attr,
        methods=methods,
        getters=getters,
        parent=parent
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


# def clean_annotations(annotations: list[tuple[str, str]], stored_strings: dict[str:str]):
#     cleaned_annotations = []
#     for annotation in annotations:
#         entry = [annotation[0]]
#         annotation_args = annotation[1]
#         string = cc.stored_string_regex.search(annotation_args)
#         while string:
#             annotation_args=annotation_args.replace(string.group(), cc.access_a_string(string.group(), stored_strings))
#             string = cc.stored_string_regex.search(annotation_args)
#         entry.append(annotation_args)
#         cleaned_annotations.append(entry)
#     return cleaned_annotations


def get_name(name_part: str, stored_strings: dict[str:str]) -> tuple[str, str | None, domain.Annotation]:
    name_part, annotations = separate_annotations(name_part, stored_strings=stored_strings)
    dataclass_annotation = annotations[0]
    name = re.search('class\s+(\w+)', name_part).group(1)
    parent = re.search('extends\s+(\w+)', name_part).group(1) if 'extends' in name_part else None
    return name, parent, dataclass_annotation


def retun_body_ast(class_body: str, class_name: str, stored_strings: str):
    bodyparts = cc.body_seperator(class_body)
    ast = [syntax_main(bp, class_name, stored_strings) for bp in bodyparts]
    getter = []
    attr = []
    methods = []
    for part in ast:
        if isinstance(part, domain.Getter):
            getter.append(part)
        elif isinstance(part, domain.Method):
            methods.append(part)
        elif isinstance(part, domain.Attribute):
            attr.append(part)
    return getter, attr, methods


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
    pre_word_regex = re.compile('(static|const|final|factory|set|external|late)\s+')  # Add more preparse words here
    syntax_characteristics = [] if return_list is None else return_list
    pre_word = pre_word_regex.match(syntax)
    if pre_word:
        cleaned_syntax = pre_word_regex.sub('', syntax, count=1)
        syntax_characteristics.append(pre_word.group(1))
        return preparse(cleaned_syntax, syntax_characteristics)
    else:
        return syntax, syntax_characteristics


def get_method_type(cleaned_method: str, keywords, classname) -> domain.MethodType:
    named_constructor_regex = re.compile(f'{classname}\.\w+')
    operator_regex = re.compile(f'{type_regex}\s+operator')
    regular_constructor_regex = re.compile(f'^{classname}\s*\(')
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
    """
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


def getter_or_attr(cleaned_attr, annotations, keywords, stored_strings) -> domain.Getter | domain.Attribute:
    getter_regex = re.compile(f'{type_regex}\s+get')
    if getter_regex.match(cleaned_attr):
        return parse_getter(cleaned_attr, annotations, keywords)
    return parse_attr(cleaned_attr, annotations, keywords, stored_strings)
    # return Getter with type and name


def get_type_and_name(unpackable) -> tuple[domain.Type, str]:
    type_, name = unpackable
    return domain.Type.from_isolated_string(type_), name.strip()


def parse_getter(getter: str, annotations: list[str], keywords: list[str]) -> domain.Getter:
    getter_metadata = re.split('=>|\{', getter)[0]
    type_, name = get_type_and_name(getter_metadata.split('get'))
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
    type_, name = get_type_and_name(re.split('\s+', attr))
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


def cut_method_body(method) -> tuple[str, str]:
    result = (method.rsplit(')', 1)[0] + ')').split('(', 1)
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
        type_, name = get_type_and_name([i.strip() for i in method.split('operator')])
    generics_match = re.search('(<(?:[^<>]+|<(?:[^<>]+|<[^<>]*>)*>)*>)$', method)
    generics = None
    if generics_match:
        generics = generics_match.group()
        method = method.replace(generics, '').strip()
    if method_type == domain.MethodType.named_constructor or method_type == domain.MethodType.factory:
        type_ = classname
        name = method.split('.')[1]
    elif method_type == domain.MethodType.constructor:
        type_ = classname
        name = classname
    elif method_type == domain.MethodType.operator:
        pass
    elif method_type == domain.MethodType.setter:
        type_ = None
        name = method
    else:
        x = re.search(f'{type_regex}\s+(\w+)', method)
        # type_ = x.group(1) + x.group(2) if x.group(2) else x.group(1)
        type_ = x.group(1)
        print(type_)
        name = x.group(3)

    return domain.Method(
        name=name,
        return_type=type_ if isinstance(type_, domain.Type) else domain.Type.from_isolated_string(type_),
        method_type=method_type,
        static='static' in keywords,
        generics=generics,
        external='external' in keywords,
        parameters_string=method_args,
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
    enum_options = re.sub('(\((?:[^()]+|\((?:[^()]+|\([^()]*\))*\))*\))', '', enum_options)  # gets rid of nested ()
    enum_options_list = [i.strip() for i in enum_options.split(',')]
    result = []
    for option in enum_options_list:
        print('-------')
        print(option)
        if '(' in option:
            print(option[0])
            result.append(option.split('(')[0].strip())
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
