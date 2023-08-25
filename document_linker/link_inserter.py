from document_linker.pattern_handler import PatternHandler
from document_linker.document_database import DocumentDatabase
from document_linker.document_objects import Document, BaseLink


class DocumentLinkInserter:
    def __init__(self) -> None:
        self.pattenr_handler = PatternHandler()

    def html_insertion(self, html: str, document_database: DocumentDatabase) -> str:
        links = self.pattenr_handler.get_documents(html)
        html_chars = list(html)
        for document in links:
            if isinstance(document, Document):
                doc_id = document_database.get_id(number=document.number, date=document.date)
                if doc_id is not None:
                    document.update_id(doc_id)
                else:
                    continue

            if not self._check_existing_link(document.link, html):
                html_chars.insert(document.link.end, document.link.close_tag)
                html_chars.insert(document.link.start, document.link.open_tag)
        
        linked_text = ''.join(html_chars)
        return linked_text

    def _check_existing_link(self, link: BaseLink, text: str) -> bool:
        len_left = len(link.left)
        len_right = len(link.right)
        if text[link.start - len_left: link.start] == link.left \
            and text[link.end: link.end + len_right] == link.right:
            return True
        return False
    