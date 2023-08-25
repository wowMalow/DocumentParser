import re
import pymorphy2

from typing import List


class Tokenizer:
    def __init__(self) -> None:
        self.analyzer = pymorphy2.MorphAnalyzer()

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r"[\w']+|[ \W]+", text)

    def lemmatize(self, tokens: List[str]) -> List[str]:
        lemmatized = []
        for word in tokens:
            if re.match(r"[\w]+", word):
                norm_word = self.analyzer.normal_forms(word)[0]
                lemmatized.append(norm_word)
            else:
                lemmatized.append(word)
        return lemmatized

    def normalize_text(self, text: str) -> str:
        tokens = self.tokenize(text)
        return "".join(self.lemmatize(tokens))
