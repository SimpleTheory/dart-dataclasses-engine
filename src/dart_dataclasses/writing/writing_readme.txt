There are 2 parts to this project:
    Reflection
    BoilerPlate Generation

Regarding boilerplate generation:
    The following functions:
        toJson
        fromJson
        static Constructor
        toString
        operator ==
        get hashCode
        get attributes
        copyWith
    Are generated for a dataclass and replace either the @Generate tag within the class
    or the <Dataclass>...</Dataclass> tags.

    The AST parser is then re-run to generate the reflection objects for the program

The additional code generation falls into the following camps:
    code generation for the enums (fromMap, fromJson, extensions)
    reflection_lists and derived maps/lists
    dependencies for code-generation (recursiveFromIter)


TODO: Write accessory functions for reflection objects for filtering them
