from dart_dataclasses.domain import *
import dart_dataclasses.file_level.file_level as file_level
from dart_dataclasses.writing.json_serialization import *
import dart_dataclasses.writing.class_functions as cf

trial_class = file_level.file_reading_procedure_for_classes('../test_cache/class.dart')[-1]

if __name__ == '__main__':
    fun_funcs_to_try = [
        cf.constructor,
        cf.attributes,
        cf.hashcode,
        cf.equality_operator,
        cf.copy_with,
        to_json,
        from_json
    ]
    for func in fun_funcs_to_try:
        print(func(trial_class))
        print('-------------')
