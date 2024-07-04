from dart_dataclasses.utils import project_root
from dart_dataclasses.writing.class_functions import *
import dart_dataclasses.file_level.file_level as f

trial_class = \
f.file_reading(project_root() / 'tests/test_cache/trying_things_out_ari_utils_2-27-2023.dart')['dataclasses'][-1]


def test_constructor():
    assert constructor(trial_class) == 'E2({required this.a, required this.b, required this.winning, this.c}) : ' \
                                       'super(a: a, b: b, c: c);'


def test_attributes():
    assert attributes(
        trial_class) == 'Map<String, dynamic> get attributes__ => {"a": a, "b": b, "c": c, "winning": winning};'


def test_copy_with():
    assert copy_with(trial_class) == 'E2 copyWithE2(int? a, String? b, String? c, double? winning) => E2(a: a ?? ' \
                                     'this.a, b: b ?? this.b, c: c ?? this.c, winning: winning ?? this.winning);'


def test_equality_operator():
    print(equality_operator(trial_class))
    result = '@override\n' \
             'bool operator ==(Object other) =>\n' \
             '  identical(this, other) ||\n' \
             '  (other is E2 && runtimeType == other.runtimeType && equals(a, other.a) && ' \
             'equals(b, other.b) && equals(c, other.c) && equals(winning, other.winning));'
    assert equality_operator(trial_class) == result


def test_hashcode():
    result = '@override\nint get hashCode => a.hashCode ^ b.hashCode ^ c.hashCode ^ winning.hashCode;'
    assert hashcode(trial_class) == result
