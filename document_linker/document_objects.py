import re
from abc import ABC, abstractmethod
from typing import Tuple, Any, Optional
from document_linker.utils import NUMBER_CHAR


class Document:
    def __init__(self, date: Optional[str], number: str, start: int, end: int) -> None:
        self.number = self._format_number(number)
        self.date = self._transform_date(date)
        self.id = -1
        self.link = DocumentLink(start, end, self.id)

    def update_id(self, id: int):
        self.id = id
        self.link = DocumentLink(self.link.start, self.link.end, self.id)

    def _transform_date(self, date: str) -> str:
        if date:
            return "-".join([f"{int(digit):02d}" for digit in date.split(".")[::-1]])
        return None
    
    def _format_number(self, number: str) -> str:
        cleaned = re.sub(rf'{NUMBER_CHAR}\s*', '', number)
        return re.sub(r'\s*', '', cleaned)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} number {self.number} from {self.date} pos {self.link.start}-{self.link.end} id {self.id}"
    
    def __repr__(self) -> str:
        return self.__str__()


class IposChapter:
    def __init__(self, chapter: str, start: int, end: int) -> None:
        self.chapter_orig = chapter
        self.chapter = self._transform_chapter(self.chapter_orig)
        self.link = IposLink(start, end, self.chapter)  
    
    def _transform_chapter(self, chapter: str) -> str:
        under_chapter = re.sub(r'\.', '_', chapter)
        return f"#chapter{under_chapter}"
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} chapter {self.chapter_orig} pos {self.link.start}-{self.link.end}"
    
    def __repr__(self) -> str:
        return self.__str__()


class BaseLink(ABC):
    def __init__(self, start: int, end: int, content: Any) -> None:
        self.start = start
        self.end = end
        self.open_tag = self._define_open_tag(content)
        self.close_tag = self._define_close_tag(content)
        self.left, self.right = self._define_existance_method(self.open_tag, self.close_tag)

    @abstractmethod
    def _define_open_tag(self, content: Any) -> str:
        pass

    @abstractmethod
    def _define_close_tag(self, content: Any) -> str:
        pass

    @abstractmethod
    def _define_existance_method(self, open_tag: str, close_tag: str) -> Tuple[str, str]:
        pass


class DocumentLink(BaseLink):
    def __init__(self, start, end, id) -> None:
        super().__init__(start=start, end=end, content=id)

    def _define_open_tag(self, content: Any) -> str:
        return f"""<a data-mce-href="/library/e-library/document/{content}" href="/library/e-library/document/{content}">"""
    
    def _define_close_tag(self, content: Any) -> str:
        return """</a>"""
    
    def _define_existance_method(self, open_tag: str, close_tag: str) -> Tuple[str, str]:
        return open_tag[-15:], close_tag

        
class IposLink(BaseLink):
    def __init__(self, start, end, chapter) -> None:
        super().__init__(start=start, end=end, content=chapter)

    def _define_open_tag(self, content: Any) -> str:
        return f"""<a data-expl-link="true" data-expl-link-anchor="{content}" data-expl-link-doc-title=""
                    data-expl-link-target-type="ipoz" data-mce-href="document{content}"
                    href="/library/ipoz/document{content}">"""
    
    def _define_close_tag(self, content: Any) -> str:
        return """</a>"""
    
    def _define_existance_method(self, open_tag: str, close_tag: str) -> Tuple[str, str]:
        return open_tag[-15:], close_tag
