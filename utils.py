import json


def save_html(html_string: str, file_name: str) -> None:
    with open(f"{file_name}.html", 'w', encoding='utf-8') as file:
        file.write(html_string)


def load_html(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        html = file.read()
    return html

def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as file:
        json_dict = json.load(file)
    return json_dict