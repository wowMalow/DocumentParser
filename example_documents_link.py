from document_linker import DocumentLinkInserter, DocumentDatabase
from utils import load_html, load_json, save_html


if __name__ == "__main__":
    documents_json = load_json("data/documents_data.json")
    orig_html = load_html("data/ass.html")

    documents = DocumentDatabase(documents_json=documents_json)
    document_linker = DocumentLinkInserter()

    linked_html = document_linker.html_insertion(html=orig_html, document_database=documents)
    save_html(linked_html, "document_linked_ass")
