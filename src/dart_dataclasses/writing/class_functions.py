import dart_dataclasses.domain as domain


def class_functions(dart_class: domain.Class) -> str:
    """
    Generation order

    constructor
    staticConstructor
    attributes
    eq (+ hashcode)
    toString
    copyWith
    toJson
    fromJson

    """
    import dart_dataclasses.writing.json_serialization as js
    generated_code = []
    # if not check_for_bool_dataclass_args('all', dart_class):
    #     return ''

    if check_for_bool_dataclass_args('constructor', dart_class):
        generated_code.append(constructor(dart_class))

    if check_for_bool_dataclass_args('staticConstructor', dart_class):
        generated_code.append(static_constructor(dart_class))

    if check_for_bool_dataclass_args('attributes', dart_class):
        generated_code.append(attributes(dart_class))

    if check_for_bool_dataclass_args('eq', dart_class):
        if dart_class.attributes:
            generated_code.append(equality_operator(dart_class))
            generated_code.append(hashcode(dart_class))

    if check_for_bool_dataclass_args('toStr', dart_class):
        generated_code.append(to_str(dart_class))

    if check_for_bool_dataclass_args('copyWith', dart_class):
        generated_code.append(copy_with(dart_class))

    if check_for_bool_dataclass_args('toJson', dart_class):
        generated_code.append(js.to_json(dart_class))

    if check_for_bool_dataclass_args('fromJson', dart_class):
        generated_code.append(js.from_json(dart_class))
    return ('\n' * 2).join(generated_code)


def constructor(dart_class: domain.Class) -> str:
    attrs_to_initialize = list(filter(
        lambda attribute: not any([attribute.external, attribute.static, attribute.late, attribute.const]),
        dart_class.attributes
    ))
    required, defaults, null = separate_null_required(attrs_to_initialize)

    base = f'{dart_class.name}(***{"".join([f"required this.{attr.name}, " for attr in required])}' \
           f'{"".join([f"this.{attr.name} = {attr.default_value}, " for attr in defaults])}' \
           f'{", ".join([f"this.{attr.name}" for attr in null])}%%%)' \
        .replace('***', '{').replace('%%%', '}')

    end_iter = ''.join([f"\n  // TODO: initiate late attribute `{attr.name}`" for attr in dart_class.attributes if all([attr.late])])
    end = f'***{end_iter}\n%%%'.replace('***', '{').replace('%%%', '}') if end_iter else ';'

    if dart_class.parent:
        try:
            call_to_super = 'super.' + dart_class.dataclass_annotation.keyword_params['superFactory'].strip()
        except KeyError:
            call_to_super = 'super'
        super_pos, super_kwarg = separate_pos_and_kwarg_super(attrs_to_initialize)
        # print(super_pos, super_kwarg)

        parent = f'{call_to_super}({"".join([f"{pos.name}, " for pos in super_pos])}' \
                 f'{", ".join([f"{kwarg.super_param}: {kwarg.name}" for kwarg in super_kwarg])})'

        return f'{base} : {parent}{end}'
    return base + end


def static_constructor(dart_class: domain.Class) -> str:
    attrs_to_initialize = list(filter(
        lambda attribute: not any([attribute.external, attribute.static, attribute.late, attribute.const]),
        dart_class.attributes
    ))
    required, defaults, null = separate_null_required(attrs_to_initialize)

    base = f'{dart_class.name}.staticConstructor(***{"".join([f"required {attr.name}, " for attr in required])}' \
           f'{"".join([f"{attr.name} = {attr.default_value}, " for attr in defaults])}' \
           f'{", ".join([f"{attr.name}" for attr in null])}%%%)'.replace('***', '{').replace('%%%', '}')
    returns = f'{dart_class.name}({", ".join([f"{attr.name}: {attr.name}" for attr in required + defaults + null])})'
    return f'factory {base} => {returns};'


def attributes(dart_class: domain.Class) -> str:
    attr_strs = [f'"{attr.name}": {attr.name}' for attr in get_dynamic_attributes(dart_class)]
    return f'Map<String, dynamic> get attributes__ => ***{", ".join(attr_strs)}%%%;' \
        .replace('***', '{') \
        .replace('%%%', '}')


def copy_with(dart_class: domain.Class) -> str:
    dynamic_attributes = get_dynamic_attributes(dart_class, construction=True)
    null = lambda x: x if x.endswith('?') else x + '?'
    attrs_params = ", ".join([f'{null(attr.type.to_str())} {attr.name}' for attr in dynamic_attributes])
    attr_body = ", ".join([f'{attr.name}: {attr.name} ?? this.{attr.name}' for attr in dynamic_attributes])
    return f'{dart_class.name} copyWith{dart_class.name}({attrs_params}) => {dart_class.name}({attr_body});'


def equality_operator(dart_class: domain.Class) -> str:
    dynamic_attributes = get_dynamic_attributes(dart_class)
    base = f'@override\n' \
           f'bool operator ==(Object other) =>\n' \
           f'  identical(this, other) ||\n  '
    dynamic_attributes_equality = [f'equals({attr.name}, other.{attr.name})' for attr in dynamic_attributes]
    dynamics = [f'other is {dart_class.name}', 'runtimeType == other.runtimeType', *dynamic_attributes_equality]
    return f'{base}({" && ".join(dynamics)});'


def hashcode(dart_class: domain.Class) -> str:
    base = '@override\nint get hashCode => '
    body = " ^ ".join([f'{attr.name}.hashCode' for attr in get_dynamic_attributes(dart_class)])
    return base + body + ';'


def to_str(dart_class: domain.Class) -> str:
    attr_strs = [f'{attr.name}: ${attr.name}' for attr in get_dynamic_attributes(dart_class)]
    return f'@override\n' \
           f'String toString() => \'{dart_class.name}({", ".join(attr_strs)})\';' \
        .replace('***', '{') \
        .replace('%%%', '}')


# ----------------------------------------------------------------------------
# Utility Functions
def separate_null_required(attrs: list[domain.Attribute]) \
        -> tuple[list[domain.Attribute], list[domain.Attribute], list[domain.Attribute]]:
    required = list(filter(lambda attribute:
                           not attribute.type.nullable and not attribute.late and not attribute.default_value, attrs))
    defaults = list(filter(lambda attribute: attribute.default_value, attrs))
    null = list(filter(lambda attribute: attribute.type.nullable or attribute.late, attrs)) #TODO INCLUDE OR EXCLUDE LATES
    return required, defaults, null


def separate_pos_and_kwarg_super(attrs: list[domain.Attribute]) -> tuple[
    list[domain.Attribute], list[domain.Attribute]]:
    super_attrs = list(filter(lambda attribute: attribute.super_param, attrs))
    # print(list(super_attrs))
    pos = sorted(
        filter(lambda attr: attr.super_param[0] == '+', super_attrs),
        key=lambda attr: len(attr.super_param)
    )

    kwarg = list(
        filter(lambda attr: attr.super_param[0] != '+', super_attrs)
    )
    return pos, kwarg


def get_dynamic_attributes(attrs: list[domain.Attribute] | domain.Class, construction: bool = False) \
        -> list[domain.Attribute]:

    if isinstance(attrs, domain.Class):
        attrs = attrs.attributes
    if not construction:
        return list(filter(
            lambda attribute: not any([attribute.external, attribute.static, attribute.const]),
            attrs
        ))
    return list(filter(
            lambda attribute: not any([attribute.external, attribute.static, attribute.const, attribute.late]),
            attrs
        ))


def type_is_iterable(type_: domain.Type) -> bool:
    return type_.type in domain.iterable_types


def type_is_map(type_: domain.Type) -> bool:
    return 'map' in type_.type.lower()


def iterable_factory(type_: domain.Type) -> str:
    return type_.to_str() + ('.from(' if type_.type != 'Iterable' else '.castFrom(')


def check_for_bool_dataclass_args(arg_name: str, dart_dataclass: domain.Class):
    try:
        arg_value = dart_dataclass.dataclass_annotation.keyword_params[arg_name]
        return arg_value.strip().lower() == 'true'
    except KeyError:
        if arg_name != 'all':
            return check_for_bool_dataclass_args('all', dart_dataclass)
        return True


def left_pad_string(string: str, num_spaces: int, start=True) -> str:
    """
    Left pads a multiline string with spaces. (Chatgpt generated)
    """
    # Split the string into individual lines.
    lines = string.split("\n")

    # Loop over each line and add the desired number of spaces to the beginning.
    for i in range(len(lines)):
        if not start and not i:
            continue
        lines[i] = " " * num_spaces + lines[i]

    # Join the lines back together into a single string.
    padded_string = "\n".join(lines)

    return padded_string
