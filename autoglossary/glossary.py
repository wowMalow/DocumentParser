import re

from collections import defaultdict
from typing import List

from autoglossary.tokenizer import Tokenizer


class Term:
    def __init__(self, term_dict: dict, tokenizer: Tokenizer) -> None:
        self.id = term_dict.get("id")
        self.name = term_dict.get("title")
        assert self.id is not None or self.name is not None, "В исходном json глоссарии отсутствуют поля id и/или title"
        
        self.tokenizer = tokenizer
        self.term_dict = self._build_term_dict(self.name, self.id)
    
    def _build_term_dict(self, name: str, id: int) -> dict:
        lemm_name = self.tokenizer.normalize_text(name)
        mask, wordlist = self._prepare_name(lemm_name)

        rank = sum(mask)
        if rank == 0:
            prepared_terms = self._get_without_variations(wordlist)
        elif rank == 1 and mask[-1] == 1:
            prepared_terms = self._get_one_alternative(wordlist)
        else:
            prepared_terms = self._get_variations(mask, wordlist)

        term_dict = {}
        for key in prepared_terms:
            term_dict[tuple(key)] = id

        return term_dict

    def _prepare_name(self, name):
        variations_mask = []
        words = []
        patterns = "[0-9!#$%&'()«»*+,./:;<=>?@[\]^_`{|}~—\"\-]+"
        for variation, base in re.findall(r"(\([^\(\)]+?\))|\b([^\(\)]+)\b", name):
            if variation == '':
                base = re.sub(patterns, "", base)
                for word in base.split():
                    words.append(word.strip())
                    variations_mask.append(0)
            else:
                variations = variation.split(",")
                for word in variations:
                    word = re.sub(patterns, "", word)
                    words.append(word.strip())
                    variations_mask.append(1)
        return variations_mask, words
    
    def _prepare_alternatives_mask(self, mask: List[int], wordlist: List[str]):
        variations_mask = mask.copy()
        words = wordlist.copy()
        i = 1
        while i < len(variations_mask):
            if variations_mask[i] == 1:
                j = i + 1 
                while j < len(variations_mask):
                    if variations_mask[j] == 1:
                        if j > i:
                            for n in range(i, j + 1):
                                words_amount = len(words[n].split())
                                if words_amount > 1:
                                    alternatives = words[n].split() 
                                    for k, (orig_word, alternative_part) in enumerate(
                                        zip(words[i-words_amount:i], alternatives)
                                        ):
                                        if orig_word == alternative_part:
                                            alternatives.pop(k)
                                    words[n] = " ".join(alternatives)

                        i = j
                    else:
                        i = j
                        break
                    j += 1
            i += 1
        return variations_mask, words
    
    def _prepare_variations_fold(self, variations_mask: List[int], words: List[str]) -> dict:
        variations_fold = defaultdict(list)
        i = 0
        k = 0
        while i < len(variations_mask):
            if i == len(variations_mask) - 1:
                variations_fold[k] += [words[i]]
                break
            if variations_mask[i] != variations_mask[i + 1] and variations_mask[i + 1] == 1:
                if i != 0:
                    k += 1
                variations_fold[k] += [words[i]]
            elif variations_mask[i] != variations_mask[i + 1] and variations_mask[i + 1] == 0:
                variations_fold[k] += [words[i]]
                if i != 0:
                    k += 1
            elif variations_mask[i] == variations_mask[i + 1]:
                if variations_mask[i] == 0:
                    variations_fold[k] = [" ".join(variations_fold[k] + [words[i]])]
                else:
                    variations_fold[k] += [words[i]]
            i += 1
        return variations_fold
    
    def _combine_variations(self, variations_fold: dict) -> List[List[str]]:
        variations = []
        def recursive_combinations(variations_fold, i, alternative):
            if i not in variations_fold.keys():
                variations.append(alternative)
            else:
                for word in variations_fold[i]:
                    if i == 0:
                        recursive_combinations(variations_fold, i+1, alternative + word)
                    else:
                        recursive_combinations(variations_fold, i+1, alternative + " " + word)
        
        recursive_combinations(variations_fold, 0, "")
        return variations
    
    def _get_variations(self, mask, wordslist):
        variations_mask, words = self._prepare_alternatives_mask(mask, wordslist)
        variations_fold = self._prepare_variations_fold(variations_mask, words)
        return [tuple(variation.split()) for variation in self._combine_variations(variations_fold)]

    def _get_one_alternative(self, words):
        return [tuple(words[:-1])] + [tuple(words[-1].split())]

    def _get_without_variations(self, words):
        return [tuple(words)]


class Glossary:
    def __init__(self, raw_glossary: dict, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer
        self.terms = self._parse_terms(raw_glossary)
        self.dictionary = self._collect_glossary_dict()

    def _parse_terms(self, raw_glossary: dict) -> List[Term]:
        terms = []
        for item in raw_glossary:
            terms.append(Term(item, self.tokenizer))
        return terms
    
    def _collect_glossary_dict(self):
        glossary_dict = {}
        for term in self.terms:
            glossary_dict.update(term.term_dict)
        return glossary_dict
