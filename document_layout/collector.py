import re

from document_layout.extractors import (
    TitleExtractor,
    NumberExtractor,
    DateExtractor,
    AuthorExtractor,
    BodyExtractor,
    DocumentLayout,
)


class LayoutCollector:
    def collect_data(self, text: str) -> DocumentLayout:
        cleaned = self._clean_html(text)

        title = TitleExtractor()(cleaned)
        number = NumberExtractor()(cleaned)
        date = DateExtractor()(cleaned)
        author = AuthorExtractor()(cleaned)
        body_content = BodyExtractor()(cleaned)

        start = body_content.start
        end = body_content.end

        number_or_date = number or date
        if number_or_date:
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

        if author:
            if author.start > start:
                end = author.start
                author = author.content
            else:
                author = None

        content = cleaned[start: end]

        return DocumentLayout(
            number=number,
            date=date,
            author=author,
            content=self._create_page(content),
        )

    def _clean_html(self, text: str) -> str:
        cleaned = re.sub('&#160;', ' ', text)
        cleaned = re.sub(r'<(p|table|tr|div).*?>', r'<\1>', cleaned)
        cleaned = re.sub(r'<font.*?>', '', cleaned)
        cleaned = re.sub(r'</font>', '', cleaned)
        cleaned = re.sub(r'<img.*?/>', '', cleaned)
        cleaned = re.sub(r'<a.*?>', '', cleaned)
        cleaned = re.sub(r'</a>', '', cleaned)
        cleaned = re.sub(r'<span.*?>', '', cleaned)
        cleaned = re.sub(r'</span>', '', cleaned)
        cleaned = re.sub(r'<hr/>', '', cleaned)
        cleaned = re.sub(r'(<u>|</u>)', '', cleaned)
        return cleaned

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