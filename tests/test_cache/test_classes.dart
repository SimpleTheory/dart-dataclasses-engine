import './class.dart';

void main(){
  group('Yess', (){
    Yess a = Yess(address: Address(), name: 'a');
    @CreateTests(Yess, a)

    @CreateTestTemplates(Yess, a)

  });
}