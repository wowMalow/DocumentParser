import re
from typing import List

from autoglossary.tokenizer import Tokenizer


class GlossaryLink:
    def __init__(self, start, end, glossary_item_id) -> None:
        self.start = start
        self.end = end
        self.span_info = f"""data-glossary-item-id="{glossary_item_id}">"""
        self.open_span = f"""<span class="abbr" {self.span_info}"""
        self.close_span = """</span>"""


class GlossaryLinkInserter:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer

    def html_insertion(self, html: str, glossary: dict) -> str:
        link_list = self._find_glossary(html, glossary)
        for link in link_list[::-1]:
            if not self._check_existing_span(self.tokens, link):
                self.tokens.insert(link.end, link.close_span)
                self.tokens.insert(link.start, link.open_span)
        return "".join(self.tokens)
    
    def _check_existing_span(self, tokens: List[str], link: GlossaryLink) -> bool:
        left_len = len(self.tokenizer.tokenize(link.span_info))
        right_len = len(self.tokenizer.tokenize(link.close_span))
        if ''.join(tokens[link.start - left_len:link.start])[-len(link.span_info):] == link.span_info \
            and ''.join(tokens[link.end:link.end + right_len])[:len(link.close_span)] == link.close_span:
            return True
        return False
    
    def _find_glossary(self, html: str, glossary: dict):
        self.tokens = self.tokenizer.tokenize(html)
        lemmatized_tokens = self.tokenizer.lemmatize(self.tokens)

        link_list = []
        i = 0
        while i < len(lemmatized_tokens):
            start, end = 0, 0
            if re.match(r"[\w]+", lemmatized_tokens[i]):
                for termin in glossary:
                    for j, termin_part in enumerate(termin):
                        while not re.match(r"[\w]+", lemmatized_tokens[i]):
                            i += 1
                        
                        if lemmatized_tokens[i] == termin_part:
                            if start == 0:
                                start = i
                            i += 1
                        else:
                            break
                        if j == len(termin) - 1:
                            end = i
                            i -= 1
                            link_list.append(
                                GlossaryLink(start=start, end=end, glossary_item_id=glossary[termin])
                            )
            i += 1
        return link_list
