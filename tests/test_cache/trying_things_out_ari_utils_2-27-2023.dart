import 'dart:core';
import 'package:ari_utils/src/ari_utils_base.dart';
import 'package:ari_utils/src/dataclasses.dart';

Map<Type, Function> nums = {
  Wrapper: Wrapper.num_,
  Example: Example.num_
};

class Wrapper<R>{
  Function _base;

  @override
  List<int>? call ()  {}

  static int num_() => 5;

  int call1<T extends num>(T a){return 1;}
  // external static String get base => 'func';
  int hi = 5;


//<editor-fold desc="Data Methods">

  Wrapper(this._base);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Wrapper &&
          runtimeType == other.runtimeType &&
          _base == other._base);

  @override
  int get hashCode => _base.hashCode;

  @override
  String toString() {
    return 'UtilityFunction{ _base: $_base,}';
  }

  Wrapper copyWith({
    Function? base,
  }) {
    return Wrapper(base ?? _base,);
  }

  Map<String, dynamic> toMap() {
    return {
      '_base': this._base,
    };
  }

  factory Wrapper.fromMap(Map<String, dynamic> map) {
    return Wrapper(map['_base'] as Function,);
  }

//</editor-fold>
}

@Dataclass(toJson: false, fromJson: false)
class Example{
  int a;
  String b;
  String? c;
  external int d;
  static int num_() => 6;


//<editor-fold desc="Data Methods">

  Example({
    required this.a,
    required this.b,
    this.c,
  });


  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Example &&
          runtimeType.toString() == other.runtimeType.toString() &&
          a.runtimeType == other.a.runtimeType &&
          a.toString() == other.a.toString() &&
          b.runtimeType == other.b.runtimeType &&
          b.toString() == other.b.toString() &&
          c.runtimeType == other.c.runtimeType &&
          c.toString() == other.c.toString());

  @override
  int get hashCode => a.hashCode ^ b.hashCode ^ c.hashCode;

  @override
  String toString() {
    return 'Example{'
        'a: $a'
        'b: $b'
        'c: $c}';
  }

  Example copyWith({
    int? a_,
    String? b_,
    String? c_,
  }) {
    return Example(a: a_ ?? a, b: b_ ?? b, c: c_ ?? c);
  }

  Map<String, dynamic> toMap() {
    return {
      'a': a,
      'b': b,
      'c': c,
    };
  }

  factory Example.fromMap(Map<String, dynamic> map) {
    return Example(
      a: map['a'] as int,
      b: map['b'] as String,
      c: map['c'] as String,
    );
  }

//</editor-fold>
}
@Dataclass()
class E2 extends Example{
  @Super('a')
  int a;
  @Super('b')
  String b;
  @Super('c')
  String? c;
  double winning;
  static const String s = 's';

  E2({required this.a, required this.b, this.c, required this.winning}) : super(a: a, b: b, c: c);
  Map get __attributes => {"a": a, "b": b, "c": c, "winning": winning};
  @override
  int get hashCode => a.hashCode ^ b.hashCode ^ c.hashCode ^ winning.hashCode;
  @override
  bool operator ==(Object other) =>
      identical(this, other) || (other is E2 && runtimeType == other.runtimeType && a == other.a && b == other.b && c == other.c && winning == other.winning);
  // E2 copyWithE2({a, b, c, winning}){
  //   return E2(a: a ?? this.a, b: b ?? this.b, winning: winning ?? this.winning);
  // }
}

enum StatusCode {
  badRequest(401, 'Bad request'),
  unauthorized(401, 'Unauthorized'),
  forbidden(403, 'Forbidden'),
  notFound(404, 'Not found'),
  internalServerError(500, 'Internal server error');

  const StatusCode(this.code, this.description);

  final int code;
  final String description;
  static const int w = 5;


  @override
  String toString() => 'StatusCode($code, $description)';
}
enum Letters {
  a,
  b,
  c;
  const Letters();

}


void main(){
  List<Type> types = [Example, Wrapper];
  for (Type type in types){
    print(nums[type]!());
  }
  // List<String> letters = ['a', 'b', 'c', 'd'];
  // List<int> numbers = [1,2,3,4];
  // Zip<String, int> zip_ = Zip.create(letters, numbers);
  // print(zip_);
  // print(zip_[0][0]);
  // for (ZipItem<String, int> i in zip_){
  //   print(i);
  // }
  // print(zip_.item1List);
  // zip_.addItem('e', 5);
  // print(zip_.contains(ZipItem('e', 5)));
  // print(zip_.containsValue(6));
  // print(zip_.containsValue(2));
  // var a = zip_.swapAll();
  // print(a.toMap());
  // List b = [2, '4', 1.2, true];
  // List c = ['y', false, [1,2], 7];
  // print(Zip.fromMap(a.toMap()));
  // print(Zip.fromEvenList(b));
  // print(Zip.create(b, c));
  // print('split');
  // print(c.splitBeforeIndex(1));
  // print('odd');
  // print(c.slice(step: 2, start: 1));
  // print('even');
  // print(c.slice(step: 2));
  // print(b[-1]);
  // print('list equals [1,2] , [1,2]');
  // print([1,2]==[1,2]);
  // print([1,2].toString());
  // print([1,2].toString()==[1,2].toString());
  // print(Logical.xand(true, true));
  // print(Logical.xand(true, false));
  // print(Logical.xand(false, true));
  // print(Logical.xand(false, false));
  print(['a', 'b'] == ['a', 'b']);
  print(1.0=='a');
  print(StatusCode.badRequest);


}