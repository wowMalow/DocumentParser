import re
from abc import ABC, abstractmethod

from typing import NamedTuple, List

from document_linker.pattern_handler import PatternHandler
from document_linker.document_objects import Document


class DocumentLayout(NamedTuple):
        title: str
        number: str
        date: str
        recipient: str
        author: str
        author_position: str
        executor: str
        content: str


class DocumentObject(NamedTuple):
        content: str
        start: int
        end: int


class BaseExtractor(ABC):
    @abstractmethod
    def __call__(self, text: str) -> DocumentObject:
        pass
    
    @classmethod
    def _clean_html(self, text: str) -> str:
        cleaned = re.sub('&#160;', ' ', text)
        cleaned = re.sub(r'<(p|table|tr|div|h1|h2|h3|h4).*?>', r'<\1>', cleaned)
        cleaned = re.sub(r'<font.*?>', '', cleaned)
        cleaned = re.sub(r'</font>', '', cleaned)
        cleaned = re.sub(r'<img.*?/?>', '', cleaned)
        cleaned = re.sub(r'</img>', '', cleaned)
        cleaned = re.sub(r'<sup>|</sup>|<sub>|</sub>', '', cleaned)
        cleaned = re.sub(r'<b>|</b>', '', cleaned)
        cleaned = re.sub(r'<a.*?>', '', cleaned)
        cleaned = re.sub(r'</a>', '', cleaned)
        cleaned = re.sub(r'<span.*?>', '', cleaned)
        cleaned = re.sub(r'</span>', '', cleaned)
        cleaned = re.sub(r'<hr/>', '', cleaned)
        cleaned = re.sub(r'(<u>|</u>)', '', cleaned)
        
        drop_duplicates = ""
        start = 0
        for doubled_obj in re.finditer(r"(<i>(.|\n)+?</i>\s*)+", cleaned):
            only_text = doubled_obj.group(0).strip()
            only_text = re.sub(r'\n|\t', ' ', only_text)
            only_text = re.sub(r'(\s)+', r'\1', only_text)
            only_text = re.sub(r"<i>|</i>", "", only_text)
            span_start, span_end = doubled_obj.span()
            drop_duplicates += cleaned[start:span_start] + "<i>" + only_text + "</i>"
            start = span_end

        drop_duplicates += cleaned[start:]
        return drop_duplicates
    
    @classmethod
    def _remove_tags(self, text: str) -> str:
        cleaned = re.sub(r"<(.|\n)*?>", '', text)
        cleaned = re.sub(r"\s+", ' ', cleaned)
        return cleaned.strip()


class AuthorExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        docs = []
        for author_obj in re.finditer(r'(([а-яА-ЯёЁ]\.\s*){2}[а-яА-ЯёЁ]+)|(([а-яА-ЯёЁ]+)([а-яА-ЯёЁ]\.\s*){2})', text):
            doc = self._prepare_author(author_obj)
            docs.append(doc)
        if len(docs) > 1:
            return docs[-2:]
        if len(docs) == 1:
            return docs[0]
        return None
    
    def _prepare_author(self, author_obj: re.Match) -> DocumentObject:
        start, end = author_obj.span()
        author = author_obj.group(0)
        author = re.sub(r'(<br/>|<p>)', '', author)
        author = re.sub(r'\s+', ' ', author)
        return DocumentObject(
                content=author,
                start=start,
                end=end,
            )
        
    

class TitleExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        # title_obj = re.search(r"(<i>(.|\n)+?</i>\s*)+", text)
        title_obj = re.search(r'<i>((.|\n)*?)</i>', text)
        if title_obj:
            start, end = title_obj.span()
            title = title_obj.group(1).strip()
            title = re.sub(r'\n|\t', ' ', title)
            title = re.sub(r'(\s)+', r'\1', title)
            title = re.sub(r"<i>|</i>", "", title)
            return DocumentObject(
                content=title,
                start=start,
                end=end,
            )
        return None
    

class BodyExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        _, body_open = re.search(r'<body(.|\n)*?>', text).span()
        body_close, _ = re.search(r'</body>', text).span()
        return DocumentObject(
            content=text[body_open: body_close],
            start=body_open,
            end=body_close,
        )


class NumberExtractor(BaseExtractor):
    pattern_handler = PatternHandler()

    def __call__(self, text: str) -> DocumentObject:
        number_date_list = self.pattern_handler._find_patterns(text=text)
        if len(number_date_list) > 0:
            number_date = number_date_list[0]
            if isinstance(number_date, Document):
                return DocumentObject(
                    content=number_date.number,
                    start=number_date.link.start,
                    end=number_date.link.end,
                )
        return None
    

class DateExtractor(BaseExtractor):
    pattern_handler = PatternHandler()

    def __call__(self, text: str) -> DocumentObject:
        number_date_list = self.pattern_handler._find_patterns(text=text)
        if len(number_date_list) > 0:
            number_date = number_date_list[0]
            if isinstance(number_date, Document):
                return DocumentObject(
                    content=number_date.date,
                    start=number_date.link.start,
                    end=number_date.link.end,
                )
        return None
