from allennlp.data.token_indexers import PretrainedBertIndexer, TokenCharactersIndexer
from chemdataextractor.nlp.allennlpwrapper import _AllenNlpTokenTagger, ProcessedTextTagger, AllenNlpWrapperTagger
from chemdataextractor.data import find_data
from .alt_tokenizers import FinetunedBertTagger, WordPieceTagger
from chemdataextractor.nlp.tag import EnsembleTagger


#BERT embeddings used as input to a BiLSTM RNN which feeds a CRF
indexers = {
    "bert": PretrainedBertIndexer(do_lowercase=False, use_starting_offsets=True, pretrained_model=find_data("models/scibert_cased_vocab-1.0.txt")),
    "token_characters": TokenCharactersIndexer(min_padding_length=3)
}

tokentagger = _AllenNlpTokenTagger()
processtagger = ProcessedTextTagger()


class _BertCRFCemTagger(AllenNlpWrapperTagger):
    tag_type = "ner_tag"
    indexers = indexers
    model = "models/bert_crf_model-1.0.tar.gz"
    overrides = {"model.text_field_embedder.token_embedders.bert.pretrained_model": find_data("models/scibert_cased_weights-1.0.tar.gz")}

    def process(self, tag):
        return tag.replace("CEM", "CM")


class BertCRFCemTagger(EnsembleTagger):
    """
    A state of the art Named Entity Recognition tagger for both organic and inorganic materials
    that uses a tagger based on BERT with a Conditional Random Field to constrain the outputs.
    More details in the paper (PAPER TO BE ADDED).
    """
    taggers = [tokentagger, processtagger, _BertCRFCemTagger()]


# A finetuned BERT model for CNER

wordpiece_tagger = WordPieceTagger(find_data("models/scibert_cased_vocab-1.0.txt"), lowercase=False)


class _FinetunedBertCemTagger(FinetunedBertTagger):
    model_name = "models/scibert_finetuned_weights-1.0"
    encoder_name = "models/scibert_cased_vocab-1.0.txt"
    lowercase = True
    tag_names = ["O", "B-CM", "I-CM"]
    tag_type = "ner_tag"


class FinetunedBertCemTagger(EnsembleTagger):
    """
    A state of the art Named Entity Recognition tagger for both organic and inorganic materials
    that uses a tagger based on BERT with a Conditional Random Field to constrain the outputs.
    More details in the paper (PAPER TO BE ADDED).
    """
    taggers = [wordpiece_tagger, _FinetunedBertCemTagger()]
