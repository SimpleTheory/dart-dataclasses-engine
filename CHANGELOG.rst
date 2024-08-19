=========
Changelog
=========
Version 0.0.2
===========
- Initial release
===========
Version 0.0.3
===========
- Bug fixed
===========
Version 0.0.4
===========
- Added {} to copyWith,
- fixed 0 attr construction bug,
- Added code for automatic update checks to pypi
- failed to implement overrides
============
Version 0.0.5
============
- Fixed bug with const attr and no type to be dynamic instead of crashing
============
Version 0.0.6
============
- Made default of @Super be the parameters own name
- Took out trinary null check operator in part declaration of fromMap as the dejsonify function in
  static takes care of it for me
- Fixed bug with `factory Singleton()=>_singletonObject` since the factory is unnamed (because it replaces
  the default constructor) I harded coded the parser to see that as the normal constructor and changed the
  reference to it's name with regard to its metadata object to `returnsSingletonObject`.
============
Version 0.0.7
============
- Modified insertion tag regex to ignore `//@Generate()` in all cases but the `//` must immediately precede
  it with no spaces, so now commented `//@Generate()` will be ignored.
- Made dynamic type to_str in the Type class not have added ?

============
Version 0.0.8
============
- Added bug fixes primarily aesthetic
- Can now comment out the generation decorators with //@ (no spaces)
- Implemented a 0th draft of test generation
============
Version 0.0.9
============
- Made enum factory from Map dynamic map because of errors and fixed bug where enum only files wouldn't be parsed
- Fixed bug where generated test insertions would come out incomplete based off the tags because the insertions would subsume each other
- Pages with only enums and no dataclasses were skipped and now they aren't
============
Version 0.0.10
============
- Introduced a few main features that have been on the backburner for a while:
    1. Introduced toApi and fromApi into the class functions (json serialization without the __type crutch)
    2. Fixed copyWith methods for it to properly clone an object by value and not by reference was done in similiar fashion to api by recursively generating the iterables and call sub copyWiths when applicable)
    3. Added crude typedef support by replacing typedef instances with the corresponding class value and having it identify types cast with it that way
- Additionally Fixed many minor bugs or other internal changes including but not limited to:
    - Parser couldn't detect truncated named constructors
    - Some function refactoring
    - Added util functions file
    - Made regex string literals to avoid new syntax warning on them
    - Added value to config file to allow for new updates, as such the config file and it's source were modified a bit
    - etc ...
============
Version 0.0.11
============
- Fixed bug with check_for_updates where when called from entry point it would crash
- Fixed a runaway regex in identifying getters that would hang the program and replaced it with a simpler funciton
- Fixed typos in cli print messages
- (Still have yet to add test generation for new functions fromApi, toApi)