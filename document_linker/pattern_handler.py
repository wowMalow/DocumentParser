import re
from typing import List, Union

from document_linker.document_objects import Document, IposChapter
from document_linker.utils import NUMBER_CHAR


class PatternHandler:
    def __init__(self) -> None:
        self.document_patterns, self.document_patterns_dict = self._init_patterns()
        self.document_patterns_regex = re.compile(self.document_patterns)

    def get_documents(self, text) -> List[Union[Document, IposChapter]]:
        return sorted(self._find_patterns(text), key=lambda x: -x.link.start)

    def _init_patterns(self) -> str:
        document_regular_pattern = r"((от)*\s*\d{1,2}\.\d{1,2}\.\d{4}\s+" + rf"{NUMBER_CHAR}+\s*[\d\w\-\/]+)"
        document_regular_pattern_inverse = rf"({NUMBER_CHAR}" + r"+\s*[\d\w\-\/]+\s+(от)*\s*\d{1,2}\.\d{1,2}\.\d{4})"

        short_pattern = rf"({NUMBER_CHAR}+\s*[\d\w\-\/]+)"

        months = r"((январ\w*)|(феврал\w*)|(март\w*)|(апрел\w*)|(ма\w*)|(июн\w*)|(июл\w*)|(август\w*)|(сентябр\w*)|(октябр\w*)|(ноябр\w*)|(декабр\w*))"
        worddate_pattern = r"\d{1,2}\s+" + months + r"\s+\d{4}\s*((год\w*)|(г\.))*"
        document_worddate_pattern = rf"(от)?\s*{worddate_pattern}(\s+{NUMBER_CHAR}+\s*[\d\w\-\/]+)"
        document_worddate_pattern_inverse = rf"({NUMBER_CHAR}+\s*[\d\w\-\/]+)\s+(от)?\s*{worddate_pattern}"

        chapter_pattern = r"((раздел\w*)|(пункт\w*)|(п\.+)|(подпункт\w*)|(пп\.+))\s*(\d+[\s,\.и]*)+"

        document_patterns_dict = {
            "regular": document_regular_pattern,
            "regular_inverse": document_regular_pattern_inverse,
            "worddate": document_worddate_pattern,
            "worddate_inverse": document_worddate_pattern_inverse,
            "short": short_pattern,
            "chapter": chapter_pattern,
        }

        return "|".join(document_patterns_dict.values()), document_patterns_dict
    
    def _find_patterns(self, text):
        documents = []
        for obj in self.document_patterns_regex.finditer(text.lower()):
            start, _ = obj.span()
            for pattern_type, pattern in self.document_patterns_dict.items():
                if re.fullmatch(pattern, obj.group(0)):
                    if pattern_type in ["regular", "regular_inverse"]:
                        document = self._handle_regular(
                            text=obj.group(0),
                            pattern_type=pattern_type,
                            global_start=start,
                        )
                    elif pattern_type in ["worddate", "worddate_inverse"]:
                        document = self._handle_worddate(
                            text=obj.group(0),
                            pattern_type=pattern_type,
                            global_start=start,
                        )
                    elif pattern_type in ["short"]:
                        document = self._handle_short(
                            text=obj.group(0),
                            pattern_type=pattern_type,
                            global_start=start,
                        )
                    elif pattern_type == "chapter":
                        document = self._handle_chapter(
                            text=obj.group(0),
                            global_start=start,
                        )
                    documents.extend(document)
        return documents
                   

    def _handle_regular(self, text: str, pattern_type: str, global_start: int) -> List[Document]:
        date_regex_object = re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", text)
        date = date_regex_object.group(0)
        start_date, end_date = date_regex_object.span()

        if pattern_type == "regular":
            offset = end_date
        elif pattern_type == "regular_inverse":
            offset = 0

        number_regex_object = re.search(rf"{NUMBER_CHAR}+\s*([\d\w\-\/]+)", text[offset:])
        number = number_regex_object.group(0)
        start_number, end_number = number_regex_object.span()

        if pattern_type == "regular":
            start = start_date
            end = end_number + end_date
        elif pattern_type == "regular_inverse":
            start = start_number
            end = end_date
        
        start += global_start
        end += global_start

        document = Document(
            date=date,
            number=number,
            start=start,
            end=end,
        )
        return [document]
    
    def _handle_short(self, text: str, pattern_type: str, global_start: int) -> List[Document]:
        number_regex_object = re.search(rf"{NUMBER_CHAR}+\s*([\d\w\-\/]+)", text)
        number = number_regex_object.group(0)
        start, end = number_regex_object.span()
        
        start += global_start
        end += global_start

        document = Document(
            date=None,
            number=number,
            start=start,
            end=end,
        )
        return [document]

    def _handle_worddate(self, text: str, pattern_type: str, global_start: int) -> List[Document]:
        months = r"((январ\w*)|(феврал\w*)|(март\w*)|(апрел\w*)|(ма\w*)|(июн\w*)|(июл\w*)|(август\w*)|(сентябр\w*)|(октябр\w*)|(ноябр\w*)|(декабр\w*))"

        date_regex_object = re.search(r"\d{1,2}\s+" + months + r"\s+\d{4}\s*((год\w*)|(г\.))*", text)
        date = date_regex_object.group(0)
        start_date, end_date = date_regex_object.span()
        for i, month in enumerate(re.findall(months, date)[0][1:]):
            if month != '':
                month_num = f"{i+1}"
                break
        date_list = re.findall(r'\d+', date)
        date_list.insert(1, month_num)
        date = '.'.join(date_list)

        if pattern_type == "worddate":
            offset = end_date
        elif pattern_type == "worddate_inverse":
            offset = 0

        number_regex_object = re.search(rf"{NUMBER_CHAR}+\s*([\d\w\-\/]+)", text[offset:])
        number = number_regex_object.group(0)
        start_number, end_number = number_regex_object.span()

        if pattern_type == "worddate":
            start = start_date
            end = end_number + end_date
        elif pattern_type == "worddate_inverse":
            start = start_number
            end = end_date
        
        start += global_start
        end += global_start

        document = Document(
            date=date,
            number=number,
            start=start,
            end=end,
        )
        return [document]

    def _handle_chapter(self, text: str, global_start: int) -> List[IposChapter]:
        chapters = []
        for chapter in re.finditer(r"((\d+\.*)+)+", text):
            start, end = chapter.span()
            start += global_start
            end += global_start
            chapter_str = chapter.group(0)

            ipoz_chapter = IposChapter(
                chapter=chapter_str,
                start=start,
                end=end
            )
            chapters.append(ipoz_chapter)
        return chapters
