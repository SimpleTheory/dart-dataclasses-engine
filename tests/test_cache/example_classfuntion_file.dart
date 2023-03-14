/// Given the below and
///    code editor is intellij
///    source file is called class.dart
///this will produce:

/// @Dataclass()
/// class Person {
///     Address address;
///     List<Person>? family;
///     String name;
/// }
/// enum Letter{
///     a,
///     b,
///     c}
///
import 'dart:convert';
import 'package:dart_dataclasses/dataclasses.dart';


// <editor-fold desc="class.dart">
import "class.dart";

extension __Person on Person{

Map get attributes__ => {"address": address, "family": family, "name": name};

@override
int get hashCode => address.hashCode ^ family.hashCode ^ name.hashCode;

@override
bool operator ==(Object other) =>
  identical(this, other) ||
  (other is Person && runtimeType == other.runtimeType && equals(address, other.address) && equals(family, other.family) && equals(name, other.name));

Person copyWithPerson(Address? address, List<Person>? family, String? name) => Person(address: address ?? this.address, family: family ?? this.family, name: name ?? this.name);

String toJson()=>jsonEncode(toMap());
Map toMap()=> {'__type': 'Person', ...nestedJsonMap(attributes__)};

factory __Person.fromJson(String json) => __Person.fromMap(jsonDecode(json));

factory __Person.fromMap(Map map){

    Address address = jsonFactoryMap['Address']!(map['address']);
    List? family_temp = recursiveFromJsonIterable(map['family']);
    String name = map['name'];

    List<Person>? family =
      family_temp == null ? null : 
      List<Person>.from(family_temp);

    return Person(address: address, family: family, name: name);
  }
}


// <editor-fold desc="enums">
LetterFromMap(Map map){
  String value =  map['value']!;
  if (value=='Letter.a'){return Letter.a;}
  if (value=='Letter.b'){return Letter.b;}
  if (value=='Letter.c'){return Letter.c;}
}
LetterFromJson(String json)=>LetterFromMap(jsonDecode(json));
// </editor-fold>
// </editor-fold>