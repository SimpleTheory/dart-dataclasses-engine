import re
from pathlib import Path
import dart_dataclasses.writing.generate_tests as test_gen
import dart_dataclasses.insertion.insertions as insert
from dart_dataclasses import domain
import dart_dataclasses.parsing.config_file as conf
from dart_dataclasses.file_level.cmd_line_level import format_file

known_old = re.compile(r'(?<!//)@(CreateTests)\(\s*(\w+),\s*[\'"](\w+)[\'"]\)(.*?)}\);\n}(?=\n)', re.DOTALL)
known_new = re.compile(r'(?<!//)@(CreateTests)\(\s*(\w+),\s*[\'"](\w+)[\'"]\)', re.DOTALL)
template_old = re.compile(r'(?<!//)@(CreateTestTemplates)\(\s*(\w+),\s*[\'"](\w+)[\'"]\)\s+(.*?)}\);\n}(?=\n)', re.DOTALL)
template_new = re.compile(r'(?<!//)@(CreateTestTemplates)\(\s*(\w+),\s*[\'"](\w+)[\'"]\)', re.DOTALL)

# ORDER FOR THIS LIST IS CRITICAL!!!
# known_old is 1st because otherwise the new will overwrite the old
# known_new is 2nd because if template_old was 2nd it would eat the generated code as
#   template_old matches with template_new + known_generation
regexes = [known_old, known_new, template_old,  template_new]

# GROUPS
# 1 Type, 2 Class, 3 Reference, 4 Content if old

def tag_type(match: re.Match) -> test_gen.TestType:
    if match.group(1) == 'CreateTests':
        return test_gen.TestType.known
    return test_gen.TestType.template

def find_match(file_content: str) -> re.Match | None:
    for regex in regexes:
        potential_match = regex.search(file_content)
        if potential_match:
            # print(regex.pattern)
            return potential_match
    return None


def file_level_test_insertion(file: Path, dataclasses: dict[str: domain.Class]):
    file_content = file.read_text()
    match = find_match(file_content)
    while match:
        tag = insert.Tag.create_general(match)
        file_content = tag.replace_with(
            file_content,
            test_gen.gen_tests,
            tag_type(match),
            dataclasses[match.group(2)],
            match.group(3),
        )
        match = find_match(file_content)
    file_content = file_content\
        .replace('Cr8Tests', 'CreateTests')\
        .replace('Cr8TestTemplates', 'CreateTestTemplates')

    insert.insert_imports_if_not_there(file)
    if not re.search(r'''import ["']package:test/test.dart['"];''', file_content):
        file_content = "import 'package:test/test.dart';\n" + file_content
    if not re.search(insert.get_metadata_import_str(), file_content):
        file_content = insert.get_metadata_import_str() + file_content
    if not re.search(r'''import ["']dart:convert['"];''', file_content):
        file_content = "import 'dart:convert';\n" + file_content

    # print(file_content)
    # Replace with write
    with open(file, 'w') as f:
        f.write(file_content)
    if conf.format_files_with_insertion:
        format_file(file)
