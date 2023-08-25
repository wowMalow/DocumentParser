# Document parser

Tools for parsing html pages with regex

## Installation

```bash
pip install -r requirements.txt
```

## Example

```python
from pprint import pprint

from document_linker import DocumentLinkInserter, DocumentDatabase
from document_layout import LayoutCollector
from utils import load_html, load_json, save_html


documents_json = load_json("data/documents_data.json")
orig_html = load_html("data/test.html")

# Layouting of document
collector = LayoutCollector()
document_layout = collector.collect_data(orig_html)

json_file = document_layout._asdict()
pprint(json_file)

# Insert existing links
documents = DocumentDatabase(documents_json=documents_json)
document_linker = DocumentLinkInserter()

linked_html = document_linker.html_insertion(
    html=orig_html, 
    document_database=documents,
)
save_html(linked_html, "document_linked_test")

```