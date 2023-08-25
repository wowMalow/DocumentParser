import re
from abc import ABC, abstractmethod

from typing import NamedTuple

from document_linker.pattern_handler import PatternHandler


class DocumentLayout(NamedTuple):
        number: str
        date: str
        author: str
        content: str


class DocumentObject(NamedTuple):
        content: str
        start: int
        end: int


class BaseExtractor(ABC):
    @abstractmethod
    def __call__(self, text: str) -> DocumentObject:
        pass


class AuthorExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        author_candidates = list(re.finditer(r'(<br/>|<p>)(([а-яА-ЯёЁ]\.\s*){2}[а-яА-ЯёЁ]+)|(([а-яА-ЯёЁ]+)([а-яА-ЯёЁ]\.\s*){2})', text))
        if len(author_candidates) > 0:
            author_obj = author_candidates.pop()
            start, end = author_obj.span()
            author = author_obj.group(0)
            author = re.sub(r'(<br/>|<p>)', '', author)
            author = re.sub(r'\s+', ' ', author)
            return DocumentObject(
                content=author,
                start=start,
                end=end,
            )
        return None
    

class TitleExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        title_obj = re.search(r'<i>((.|\n)*)</i>', text)
        if title_obj:
            start, end = title_obj.span()
            title = title_obj.group(1).strip()
            title = re.sub(r'\n', ' ', title)
            return DocumentObject(
                content=title,
                start=start,
                end=end,
            )
        return None
    

class BodyExtractor(BaseExtractor):
    def __call__(self, text: str) -> DocumentObject:
        _, body_open = re.search(r'<body(.|\n)*>', text).span()
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
        if number_date.number and len(number_date.number) > 0:
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
        if number_date.date and len(number_date.date) > 0:
            return DocumentObject(
                content=number_date.date,
                start=number_date.link.start,
                end=number_date.link.end,
            )
        return None
