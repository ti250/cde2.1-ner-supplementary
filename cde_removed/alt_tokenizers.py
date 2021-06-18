import spacy
from chemtok import ChemTokeniser
from chemdataextractor.nlp.tokenize import WordTokenizer, ChemWordTokenizer


class SpacyTokenizer(ChemWordTokenizer):
    def __init__(self, split_last_stop=True):
        super().__init__(split_last_stop)
        self.nlp = spacy.load("en_core_web_sm")
        self.tokenizer = self.nlp.Defaults.create_tokenizer(self.nlp)

    def span_tokenize(self, s, additional_regex=None):
        tokens = self.tokenizer(str(s))
        spans = [(token.idx, token.idx + len(token)) for token in tokens]

        cleaned_spans = []
        for index, span in enumerate(spans):
            if s[span[0]: span[1]] == " ":
                pass
            elif index != len(spans) - 1 and s[span[0]: span[1]] == "." and s[span[0] - 1: span[0]] != " ":
                cleaned_spans[-1] = (cleaned_spans[-1][0], cleaned_spans[-1][1] + 1)
            else:
                cleaned_spans.append(span)
        return cleaned_spans


class ChemTokWordTokenizer(WordTokenizer):
    def span_tokenize(self, s, additional_regex=None):
        s = str(s)
        tokens = ChemTokeniser(s, clm=True, aggressive=False).tokens
        spans = [(token.start, token.end) for token in tokens]
        return spans
