from collections import defaultdict
from typing import Union


class DocumentDatabase:
    def __init__(self, documents_json: dict) -> None:
        self.dictionary = self._create_index(documents_json)

    def get_id(self, number: str, date: str) -> Union[int, None]:
        db_index = self.dictionary.get(number.lower())
        if db_index is not None:
            doc_id = db_index.get(date)
            if doc_id is None:
                doc_id = db_index.get("id")
            return doc_id
        else:
            return None

    def _create_index(self, documents_json):
        documents_search_dict = defaultdict(dict)
        for doc in documents_json:
            number = doc.get("number")
            if number is not None:
                date = doc.get("date")
                doc_id = doc.get("id")
                if date is not None:
                    documents_search_dict[number.lower()].update({date: doc_id})
                documents_search_dict[number.lower()].update({"id": doc_id})
        return documents_search_dict