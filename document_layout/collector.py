import re

from document_layout.extractors import (
    BaseExtractor,
    TitleExtractor,
    NumberExtractor,
    DateExtractor,
    AuthorExtractor,
    BodyExtractor,
    DocumentLayout,
)


class LayoutCollector:
    def collect_data(self, text: str) -> DocumentLayout:
        cleaned = BaseExtractor._clean_html(text)

        title = TitleExtractor()(cleaned)
        number = NumberExtractor()(cleaned)
        date = DateExtractor()(cleaned)
        authors = AuthorExtractor()(cleaned)
        body_content = BodyExtractor()(cleaned)
        
        author = None
        executor = None
        recipient = None
        author_position = None

        start = body_content.start
        end = body_content.end

        number_or_date = number or date
        if number_or_date:
            recipient = cleaned[start: number_or_date.start]
            recipient = BaseExtractor._remove_tags(recipient)
            start = number_or_date.start

        if number:
            number = number.content

        if date:
            date = date.content
        
        if title:
            if title.start < start:
                number = None
                date = None
            else:
                start = title.end
            title = title.content

        if authors:
            if isinstance(authors, list):
                author, executor = authors
                if author.start > start:
                    author_position = re.split(r"<p><br/>\s*</p>", cleaned[:author.start]).pop()
                    end = author.start - len(author_position)
                    
                    author = author.content
                    executor = executor.content
                    author_position = BaseExtractor._remove_tags(author_position)
                else:
                    author = None
                    executor = None
            else:
                executor = authors
                if executor.start > start:
                    end = executor.start
                    executor = executor.content
                else:
                    executor = None
                author = None

        content = cleaned[start: end]

        return DocumentLayout(
            title=title,
            number=number,
            date=date,
            recipient=recipient,
            author=author,
            author_position=author_position,
            executor=executor,
            content=self._create_page(content),
        )

    def _create_page(self, content: str) -> str:
        html_start = """<!DOCTYPE html>
        <html data-mce-style="height: auto;" style="height: auto;">
        <head>
            <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
        </head>
        <body>
        """
        html_end = """</body></html>"""
        return html_start + content + html_end