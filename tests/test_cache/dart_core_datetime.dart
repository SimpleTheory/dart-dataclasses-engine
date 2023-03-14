@Dataclass()
class bool {


  // The .fromEnvironment() constructors are special in that we do not want
  // users to call them using "new". We prohibit that by giving them bodies
  // that throw, even though const constructors are not allowed to have bodies.
  // Disable those static errors.
  //ignore: const_constructor_with_body
  //ignore: const_factory
  external const factory bool.fromEnvironment(String name,
      {bool defaultValue = false});


  // The .hasEnvironment() constructor is special in that we do not want
  // users to call them using "new". We prohibit that by giving them bodies
  // that throw, even though const constructors are not allowed to have bodies.
  // Disable those static errors.
  //ignore: const_constructor_with_body
  //ignore: const_factory
  external const factory bool.hasEnvironment(String name);

  external int get hashCode;


  @Since("2.1")
  bool operator &(bool other) => other && this;


  @Since("2.1")
  bool operator |(bool other) => other || this;


  @Since("2.1")
  bool operator ^(bool other) => !other == this;


  String toString() {
    return this ? "true" : "false";
  }
}
