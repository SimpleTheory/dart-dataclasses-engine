from dart_dataclasses.writing.class_functions import *
from dart_dataclasses.file_level.file_level import file_reading_procedure_for_classes

trial_class = file_reading_procedure_for_classes(r'D:\StudioProjects\ari_utils\test\trying_things.dart')[1]


def test_constructor():
    assert constructor(trial_class) == 'E2({required this.a, required this.b, required this.winning, this.c}) : ' \
                                       'super(a: a, b: b, c: c);'

def test_attributes():
    assert attributes(trial_class) == 'Map get __attributes => {"a": a, "b": b, "c": c, "winning": winning};'


def test_copy_with():
    assert copy_with(trial_class) == 'E2 copyWithE2(int? a, String? b, String? c, double? winning) => E2(a: a ?? ' \
                                     'this.a, b: b ?? this.b, c: c ?? this.c, winning: winning ?? this.winning);'

def test_equality_operator():
    print(equality_operator(trial_class))
    result = '@override\nbool operator ==(Object other) =>\n  identical(this, other) || (other is E2 && runtimeType ' \
             '== other.runtimeType && equals(a, other.a) && equals(b, other.b) && equals(c, other.c) && equals(' \
             'winning, other.winning));'
    assert equality_operator(trial_class) == result


def test_hashcode():
    result = '@override\nint get hashCode => a.hashCode ^ b.hashCode ^ c.hashCode ^ winning.hashCode;'
    assert hashcode(trial_class) == result

def test_get_type_casting_line():
    test_type = domain.Type.from_isolated_string('Map<int, Queue<List<String>>>')
    assert get_type_casting_line(test_type) == [
        domain.Type.from_isolated_string('Map<int, Queue<List<String>>>'),
        domain.Type.from_isolated_string('Queue<List<String>>'),
        domain.Type.from_isolated_string('List<String>')
    ]
