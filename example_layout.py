from pprint import pprint
from document_layout import LayoutCollector
from utils import load_html, save_html


if __name__ == "__main__":
    orig_html = load_html("data/converted_html/01.htm")

    collector = LayoutCollector()
    document_layout = collector.collect_data(orig_html)

    json_file = document_layout._asdict()
    pprint(json_file)

    save_html(document_layout.content, "only_content")
