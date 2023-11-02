from pathlib import Path
from dart_dataclasses import domain
from dart_dataclasses.writing.class_functions import left_pad_string
import dart_dataclasses.parsing.config_file as conf
import re
import functools

static = '''

// All together

List<SupportedClasses> reflectedClasses = [...dataclasses,  ...supportedDefaults, ...enumExtensions];
Map<String, SupportedClasses> str2reflection = {...str2dataclasses, ...str2defaults, ...str2enumExtensions};
Map<Type, SupportedClasses> type2reflection = {...type2dataclasses, ...type2defaults, ...type2enumExtensions};

// Deserialize JSON

dejsonify(thing){
  // Map or Recognized
  if (thing is Map){
    // Recognized
    if (str2reflection[thing['__type']]?.fromMap != null){
      return str2reflection[thing['__type']]!.fromMap!(thing);
    }
    // Map
    return dejsonifyMap(thing);
  }
  // List
  if (thing is List){
    return dejsonifyList(thing);
  }
  // Json safe type
  return thing;
}
List dejsonifyList(List list){
  return list.map((e) => dejsonify(e)).toList();
}
Map dejsonifyMap(Map map){
  return Map.from(map.map((key, value) =>
      MapEntry(dejsonify(key), dejsonify(value))));
}

// Serialize JSON

jsonify(thing) {
    if (isJsonSafe(thing)) {
      return thing;
    }
    else if (supportedTypeToMap(thing) != null){
      return supportedTypeToMap(thing);
    }
    else if (thing is Iterable && !isMap(thing)) {
      return nestedJsonList(thing);
    }
    else if (isMap(thing)) {
      return nestedJsonMap(thing);
    }
    else {
      return thing.toMap();
    //  throw Exception('Error on handling $thing since ${thing.runtimeType} '
    //      'is not a base class or does not have a toJson() method');
    }
}


List nestedJsonList(Iterable iter) {
  List l = [];
  for (var thing in iter) {
    l.add(jsonify(thing));
  }
  return l;
}

Map nestedJsonMap(mapLikeThing) {
  Map m = {};
  var key;
  var value;

  for (MapEntry mapEntry in mapLikeThing.entries) {
    key = jsonify(mapEntry.key);
    value = jsonify(mapEntry.value);
    m[key] = value;
  }

  return m;
}
'''

def pop_lib(import_str: str):
    if re.search(r'package:\w+\/lib', import_str):
        return import_str.replace('/lib', '', 1)
    else:
        return import_str

def pop_lib_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            return pop_lib(result)
        else:
            iteration_type = type(result)
            return iteration_type([pop_lib(i) for i in result])
    return wrapper
@pop_lib_decorator
def get_local_imports(file: Path) -> set[str]:
    content = file.read_text()
    return set([i.strip() for i in re.findall(r'\s*import\s+[\'\"][^;]+;', content)])
@pop_lib_decorator
def fix_import(file: Path):
    # import 'package:my_project/lib/my_library.dart';
    relation = str(file.relative_to(conf.cwd.parent)).replace('\\', '/')
    return f'import \'package:{relation}\';'

def class_groupings(file_dataclasses: dict[Path: dict[str:list[domain.Class] | list[domain.Enum]]]) \
        -> dict[str: set[str]]:
    # Class type must be either or Dataclass
    final_dict = {
        'imports': {"import 'package:dataclasses/dataclasses.dart';"},
        'dataclasses': set(),
        'enums': set(),
    }
    for file, groups in file_dataclasses.items():
        if not groups:
            continue
        final_dict['imports'].add(fix_import(file))
        final_dict['imports'] = final_dict['imports'].union(get_local_imports(file))
        for key, group in groups.items():
            if not group:
                continue
            final_dict[key] = final_dict[key].union([cls.to_dart() for cls in group])
    try:
        from dart_dataclasses.insertion.insertions import get_metadata_import_str
        final_dict['imports'].remove(get_metadata_import_str())
    except KeyError:
        pass
    return final_dict


def conjoin_str(groups_dict: dict[str:set[str]]) -> dict[str:str]:
    new_map = {}
    for key in groups_dict.keys():
        joiner = ',\n'
        if key == 'imports':
            joiner = '\n'
        new_map[key] = joiner.join(groups_dict[key])
    return new_map

def dynamic_lists(conjoined_dict: dict[str:str]) -> str:
    return f'''
List<ReflectedClass> dataclasses = [
{left_pad_string(conjoined_dict['dataclasses'], 4)}
  ];
List<EnumExtension> enumExtensions = [
{left_pad_string(conjoined_dict['enums'], 4)}
  ];
    '''.strip()

def accessory_maps(map_names=None) -> str:
    lst=[]
    if not map_names: map_names = ['dataclasses', 'enumExtensions']
    for name in map_names:
        type_ = 'ReflectedClass' if name != 'enumExtensions' else 'EnumExtension'
        lst.append(f'Map<String, {type_}>str2{name} = {{for ({type_} x in {name}) x.name: x}};')
        lst.append(f'Map<Type, {type_}>type2{name} = {{for ({type_} x in {name}) x.referenceType.referenceType!: x}};')
        lst.append('\n')
    return '\n'.join(lst).rstrip()

def generate_metadata_text(file_dataclasses: dict[Path: dict[str:list[domain.Class] | list[domain.Enum]]]) \
        -> str:
    """
    {imports}

    {dynamic_lists}

    {accessory_maps}

    {static}
    """
    strings_dict = conjoin_str(class_groupings(file_dataclasses))
    return f'''
{strings_dict['imports']}


{dynamic_lists(strings_dict)}

{accessory_maps()}
{static}
'''.strip()

def write_metadata_file(file_dataclasses: dict[Path: dict[str:list[domain.Class] | list[domain.Enum]]]):
    from dart_dataclasses.parsing.config_file import output_path
    from dart_dataclasses.file_level.cmd_line_level import format_file
    metadata_file = output_path.joinpath('metadata.dart')
    with open(metadata_file, 'w') as f:
        f.write(generate_metadata_text(file_dataclasses))
    format_file(metadata_file)
