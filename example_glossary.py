from autoglossary import Glossary, GlossaryLinkInserter
from autoglossary.tokenizer import Tokenizer
from utils import load_html, load_json, save_html

if __name__ == "__main__":
    raw_glossary = load_json("data/glossary.json")
    orig_html = load_html("data/ass.html")

    tokenizer = Tokenizer()
    glossary = Glossary(raw_glossary, tokenizer)
    glossary_inserter = GlossaryLinkInserter(tokenizer)

    linked_html = glossary_inserter.html_insertion(html=orig_html, glossary=glossary.dictionary)
    save_html(linked_html, "linked_ass")
