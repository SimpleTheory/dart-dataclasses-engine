from dart_dataclasses.writing.generate_tests import *
import dart_dataclasses.file_level.file_level as file_stuff
trial_class2: domain.Class = file_stuff.file_reading(r'D:\PycharmProjects\dart_dataclasses\tests\test_cache\class.dart')['dataclasses'][-1]

def test_known():
    print()
    result = base_known_tests(trial_class2, 'a')
    expected = '''  test('Yess.toString()', (){
      String expectation = 'Yess(address: ${a.address}, family: ${a.family}, name: ${a.name})';
      expect(a.toString(), expectation);
  });
  
  test('Yess.toMap()', (){
          Map<String, dynamic> expectation = {"__type": "Yess", "address": a.address, "family": a.family, "name": a.name};
          expect(a.toMap(), expectation);
      });
  
  test('Yess == and copyWith', (){
          Yess copy = a.copyWithYess();
          bool eq = a == copy;
          expect(eq, true);
          expect(copy, a);
      });
  
  test('Yess.toJson()', (){
          String expectation = jsonEncode(a.toMap());
          expect(a.toJson(), expectation);
      });
  
  test('Yess.fromMap() and ==', (){
          Map<String, dynamic> map = a.toMap();
          Yess expectation = Yess.fromMap(map);
          expect(a, expectation);
      });
  
  test('Yess.fromJson() and ==', (){
          String json = a.toJson();
          Yess expectation = Yess.fromJson(json);
          expect(a, expectation);
      });
  
  test('Yess.staticConstructor()', (){
          Yess expectation = Yess.staticConstructor(address: a.address, family: a.family, name: a.name);
          expect(Yess.staticConstructor(address: a.address, family: a.family, name: a.name).runtimeType, Yess);
      });'''
    # print(result)
    # print('-------------------------------------------------')
    assert result == expected

def test_template():
    result = base_template_tests(trial_class2, 'a')
    expected = '''  
  test('Yess.someFunc',(){
    // TODO: complete test
    // a.someFunc();
    // expect(result, expectation);
  });
  
  
  test('Yess.smiley',(){
    // TODO: complete test
    // String result = Yess.smiley();
    // expect(result, expectation);
  });
  
  
  test('Yess.sad',(){
    // TODO: complete test
    // String result = a.sad();
    // expect(result, expectation);
  });
  
  
  test('Yess.+',(){
    // TODO: complete test
    // Yess result = a + ;
    // expect(result, expectation);
  });'''
    print(result)
    assert result == expected
