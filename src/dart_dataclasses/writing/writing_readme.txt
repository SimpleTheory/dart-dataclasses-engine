Fundamentally there are 3 files that need to be written:
    - The extensions on the dataclasses themselves
    - Metadata regarding the Classes
    - A library declaration that glues together the class definitions, the extensions, and the metadata file.

The extensions should be:
    organized by file alphabetically (using editor-fold="", //region desc //endregion, # --- Desc ------------)
    organized by class therein alphabetically
    the functions to write are as follows: (functions should also be organized alphabetically under classes)
        toJson (hard, cascading issue and nesting issue)
        fromJson (hard, ^)
        toString
        operator ==
        get hashCode
        get attributes
        copyWith

        constructor(in file proper)(has to find where to place constructor)



