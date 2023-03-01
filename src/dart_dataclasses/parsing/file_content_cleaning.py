import re
stored_string_regex = re.compile('____\w+_\w+:\d+____')

def substitute_strings(file_content: str) -> tuple[str, dict[str:str]]:
    """
    Replace order:
        '''
        \"\"\"
        "
        \'
        '
    Restore order should be reverse of this.
    :param file_content:
    :return:
    """
    stored_strings = {}
    multi = '\'\'\'[\s\S]+?\'\'\''
    single = '\'.*?\''

    # multi-line '''
    stored_strings['multiline_single'] = re.findall(multi, file_content)

    # multi-line """
    stored_strings['multiline_double'] = re.findall(multi.replace('\'', '"'), file_content)

    # single-line "
    stored_strings['singleline_double'] = re.findall(single.replace('\'', '"'), file_content)

    # escapes \'
    stored_strings['escapes_char'] = re.findall(r'\\\'', file_content)

    # single-line '
    stored_strings['singleline_single'] = re.findall(single, file_content)

    for key, match_list in stored_strings.items():
        for i, string in enumerate(match_list):
            file_content = file_content.replace(string, f'____{key}:{i}____', 1)
    return file_content, stored_strings


def restore_strings(file_content: str, stored_strings: dict[str:str]) -> str:
    for key, match_list in stored_strings.items().__reversed__():
        for match in re.findall(f'____{key}:\d+____', file_content):
            index = int(re.search('\d+', match).group())
            file_content = file_content.replace(match, match_list[index])
    return file_content


def remove_comments(code):
    # Regular expression to match single-line comments (// ...)
    pattern1 = r"\/\/.*?$"

    # Regular expression to match multi-line comments (/* ... */)
    pattern2 = r"\/\*[\s\S]*?\*\/"
    pattern3 = r'^\/\/\/.+'

    # Remove comments from code using regular expressions
    code_without_comments = re.sub(pattern1, "", code, flags=re.MULTILINE)
    code_without_comments = re.sub(pattern2, "", code_without_comments)
    code_without_comments = re.sub(pattern3, "", code_without_comments)

    return code_without_comments


def clean_file(file) -> tuple[str, dict[str:str]]:
    with open(file, 'r') as f:
        file_content = f.read()
    subbed, stored_strings = substitute_strings(file_content)
    removed = remove_comments(subbed)
    return removed, stored_strings


def isolate_marked_classes(file_content):
    class_isolates = ['@dataclass' + i.strip() for i in re.split('@Dataclass', file_content)[1:]]
    return class_isolates

def isolate_enums(file_content):
    # \s*enum\s+\w+\s*(?=\{)
    class_isolates = [i.strip() for i in re.split('\s*enum\s+', file_content)[1:]]
    return class_isolates

def restore_strings_while_loop(source: str, stored_strings: dict[str:str]) -> str:
    string = stored_string_regex.search(source)
    while string:
        source = source.replace(
            string.group(), access_a_string(string.group(), stored_strings)[1:-1])
        string = stored_string_regex.search(source)
    return source
def get_class_isolates(file_content):
    class_chunks = isolate_marked_classes(file_content)
    class_isolates = [clean_class_from_isolate_chunk(i) for i in class_chunks]
    return class_isolates
def get_enums(file_content):
    enum_chunks = isolate_enums(file_content)
    enum_isolates = [clean_class_from_isolate_chunk(i) for i in enum_chunks]
    return enum_isolates

def clean_class_from_isolate_chunk(class_iso_chunk: str) -> tuple[str, str]:
    start = False
    bracket_cnt = 0
    name_final_index = 0
    body_final_index = 0

    for index, char in enumerate(class_iso_chunk):
        if char == '{':
            bracket_cnt += 1
            if start is False:
                start = True
                name_final_index = index
        if char == '}':
            bracket_cnt -= 1
            if start and not bracket_cnt:
                body_final_index = index + 1
                break

    name = class_iso_chunk[:name_final_index].strip()
    body = class_iso_chunk[name_final_index : body_final_index]

    return name, body


def access_a_string(key, stored_strings):
    key = key.replace('____', '')
    key, index = key.split(':')
    index = int(index)
    return stored_strings[key][index]

def body_seperator(body: str) -> list[str]:
    separation = []
    split_points = []
    body = body[1:-1].strip()
    bracket_cnt = 0
    embed = 0
    for index, char in enumerate(body):
        try:
            next_char = body[index + 1]
        except IndexError:
            next_char = None
        if char == '(':
            embed += 1
        if char == ')':
            embed -= 1
        if char == ';' and not bracket_cnt and not embed:
            split_points.append(index)
        if char == '{':
            bracket_cnt += 1
        if char == '}':
            bracket_cnt -= 1
            if all([not bracket_cnt, not embed, next_char != ';']):
                split_points.append(index)
    for i, point in enumerate(split_points):
        if i == 0:
            separation.append(body[:point+1].strip())
            last_point = point+1
            continue
        elif len(split_points) - 1 == i:
            separation.append(body[last_point:].strip())
            break
        else:
            separation.append(body[last_point:point+1].strip())
            last_point = point+1
    # if separation[-1] == ';':
    #     separation = separation[:-1]
    #     separation[-1] += ';'
    return separation


if __name__ == '__main__':
    b, strings = clean_file(r'D:\StudioProjects\ari_utils\lib\src\ari_utils_base.dart')
    b = isolate_marked_classes(b)
    class_names_and_bodies = [clean_class_from_isolate_chunk(chunk) for chunk in b]
    x = [body_seperator(class_[1]) for class_ in class_names_and_bodies]
    pass
