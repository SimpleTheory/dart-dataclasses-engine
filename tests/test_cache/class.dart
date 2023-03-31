@Dataclass()
class Zip<I1, I2> extends DelegatingList<ZipItem<I1 ,I2>>{
  @Super('+')
  final List<ZipItem<I1,I2>> _base;
  Zip(this._base) : super(_base);

  void addItem(I1 item1, I2 item2){
    _base.add(ZipItem(item1, item2));
  }
  Zip<I1, I2> extendItems(List<I1> a, List<I2> b){
    return Zip.create(item1List+a, item2List+b);
  }

  List<I1> get item1List => _base.map<I1>((e) => e[0]).toList();
  List<I2> get item2List => _base.map<I2>((e) => e[1]).toList();

  factory Zip.create(List<I1> a, List<I2> b){
    if (a.length == b.length){
      List<ZipItem<I1, I2>> baseList = [];
      for (int i in range(a.length)){
        baseList.add(ZipItem(a[i], b[i]));
      }
      return Zip(baseList);
    }
    throw ArgumentError('Length A != Length B\n${a.length} != ${b.length}');
  }
  factory Zip.fromEvenList(List list){
    if (list.length % 2 != 0)
    {throw ArgumentError('List must be even current at ${list.length}');}
    List<ZipItem<I1, I2>> newBaseList = [];
    for (EnumListItem enumItem in enumerateList(list)){
      if (enumItem.i + 1 > list.length) {break;}
      else if(enumItem.i % 2 == 1){continue;}
      else{
        newBaseList.add(ZipItem(enumItem.value, list[enumItem.index+1]));
      }
    }
    return Zip(newBaseList);
  }
  factory Zip.fromMap(Map map_){
    List<ZipItem<I1, I2>> newBaseList = [];
    map_.forEach((key, value) {newBaseList.add(ZipItem(key, value));});
    return Zip(newBaseList);
  }
  Zip<I2, I1> swapAll(){
    return Zip(_base.map((e) => e.swap()).toList());
  }


  bool containsValue(Object? element) {
    for (ZipItem<I1, I2> item in _base){
      if (item.item1==element){return true;}
      if (item.item2==element){return true;}
    }
    return false;
  }

}

class bruh{
const bruh();
}

@Dataclass(constructor: false)
class MyClass {
  int myField = 5;
  final String myString;

  MyClass(this.myString);

  void myMethod() {
    print('Hello, world!');
  }
  bruh(){}
  @Generate()
}

@Dataclass()
class Person {
    Address address;
    List<Person>? family;
    String name;

    @Generate()
}

class Address{
  const Address();
}

@Dataclass()
class Yess {
    Address address;
    List<Yess>? family;
    String name;

    void someFunc(){}
    static String smiley() => ':)';
    String sad()=>':(';

    Yess operator +(String s) => Yess.copyWithYess(name: name + s);

      // ------------------------ Dataclass Section --------------------------------
  // <Dataclass>
  
  Yess({required this.address, this.family, required this.name});
  
  factory Yess.staticConstructor({required address, family, required name}) => Yess(address: address, family: family);
  
  Map<String, dynamic> get attributes__ => {"address": address, "family": family, "name": name};
  
  @override
  bool operator ==(Object other) =>
    identical(this, other) ||
    (other is Yess && runtimeType == other.runtimeType && equals(address, other.address) && equals(family, other.family) && equals(name, other.name));
  
  @override
  int get hashCode => address.hashCode ^ family.hashCode;
  
  @override
  String toString() => 'Yess(address: $address, family: $family)';
  
  Yess copyWithYess(Address? address, List<Yess>? family, String? name) => Yess(address: address ?? this.address, family: family ?? this.family, name: name ?? this.name);
  
  String toJson()=>jsonEncode(toMap());
  Map<String, dynamic> toMap()=> {'__type': 'Yess', ...nestedJsonMap(attributes__)};
  
  factory Yess.fromJson(String json) => Yess.fromMap(jsonDecode(json));
  
  factory Yess.fromMap(Map map){    
  
      Address address = dejsonify(map['address']);
      List? familyTemp = dejsonify(map['family']);
      String name = dejsonify(map['name'])
  
      List<Yess>? family =
        familyTemp == null ? null : 
        List<Yess>.from(familyTemp);
  
      return Yess(address: address, family: family);
    }
  // </Dataclass>
      
  // ------------------------ End Dataclass Section --------------------------------)
}