#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tagger implementation for using a finetuned BERT model for token classification, e.g. for NER.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import logging
import re
import datetime

from chemdataextractor.nlp.tag import BaseTagger
from chemdataextractor.data import find_data

import torch
from transformers import BertForTokenClassification, BertTokenizer
from tokenizers import BertWordPieceTokenizer
from yaspin import yaspin


class WordPieceTagger(BaseTagger):
    tag_type = "wordpieces"

    def __init__(self, vocab_location, lowercase=True):
        self.tokenizer = BertWordPieceTokenizer(vocab_location, lowercase=lowercase)

    def tag(self, tokens):
        text_tokens = [token.processed_text for token in tokens]
        encodeds = self.tokenizer.encode_batch(text_tokens)
        tags = [encoded.tokens[1: -1] for encoded in encodeds]
        return zip(tokens, tags)


class FinetunedBertTagger(BaseTagger):
    model_name = ""
    encoder_name = ""
    tag_type = ""
    lowercase = False
    tag_names = []

    def __init__(self, model_location=None, encoder_location=None, device=None, tag_names=None, lowercase=None):
        self.model_location = model_location if model_location is not None else find_data(self.model_name)
        self.encoder_location = encoder_location if encoder_location is not None else find_data(self.encoder_name)
        self.lowercase = lowercase if lowercase is not None else self.lowercase
        self._model = None
        self._encoder = None
        self.device = device
        if tag_names is not None:
            self.tag_names = tag_names

    @property
    def model(self):
        if self._model is None:
            with yaspin(text="Initialising Transformer model", side="right").simpleDots as sp:
                self._model = BertForTokenClassification.from_pretrained(self.model_location)
                device = self.device
                if device is None and torch.cuda.is_available():
                    device = torch.cuda.current_device()
                if device is not None:
                    self._model = self._model.to(device)
                self._model = self._model.eval()
                sp.ok("✔")
        return self._model

    @property
    def encoder(self):
        if self._encoder is None:
            self._encoder = BertTokenizer.from_pretrained(self.encoder_location, do_lower_case=self.lowercase)
        return self._encoder

    def _token_wordpieces_map(self, tokens):
        slices = []
        current_index = 0
        for token in tokens:
            num_wordpieces = len(token.wordpieces)
            slices.append(slice(current_index, current_index + num_wordpieces))
            current_index += num_wordpieces
        return slices

    def _predictions_for_tokens(self, tokens, wordpiece_predictions):
        token_wordpieces_map = self._token_wordpieces_map(tokens)
        predictions = []
        for slice in token_wordpieces_map:
            predictions_for_token = wordpiece_predictions[slice]
            prediction_for_token = "O"
            for prediction in predictions_for_token:
                # Disable final or condition here to disable turning intermediates without beginnings into beginnings.
                if (prediction[0] == "B" or (prediction[0] == "I" and slice.start == 0)
                   or (prediction[0] == "I" and predictions[-1] == "O")):
                    prediction_for_token = "B-" + prediction[2:]
                    break
                elif prediction[0] == "I":
                    prediction_for_token = prediction
            # print(predictions_for_token, prediction_for_token)
            predictions.append(prediction_for_token)
        return predictions

    def tag(self, tokens):
        sentence = []
        for token in tokens:
            sentence.extend(token.wordpieces)
        encoded = self.encoder.encode(sentence, return_tensors='pt')
        with torch.no_grad():
            prediction = torch.argmax(self.model(encoded)[0], dim=2).tolist()
        prediction = [self.tag_names[index] for index in prediction[0][1: -1]]
        prediction = self._predictions_for_tokens(tokens, prediction)
        return zip(tokens, prediction)

    def batch_tag(self, sents):
        start_time = datetime.datetime.now()
        max_length = 0
        sents = sorted(sents, key=len)
        sentences = []
        for sent in sents:
            sentence = []
            for token in sent:
                sentence.extend(token.wordpieces)
            sentences.append(sentence)

        batched_sentences = []
        if len(sents) > 200:
            new_list_sequence_delta = 10
            min_batch_size = 100
            max_batch_size = 300
            current_list_min_sequence_length = len(sents[0])
            sents_current = []
            for sent in sentences:
                if (len(sent) > current_list_min_sequence_length + new_list_sequence_delta and len(sents_current) > min_batch_size) or len(sents_current) > max_batch_size:
                    batched_sentences.append(sents_current)
                    sents_current = [sent]
                    current_list_min_sequence_length = len(sent)
                else:
                    sents_current.append(sent)
            batched_sentences.append(sents_current)
        else:
            batched_sentences = [sentences]

        batch_creation_time = datetime.datetime.now()
        print("".join(["Created batches:", str(batch_creation_time - start_time)]))
        print("".join(["Maximum length of sentence:", str(max_length)]))
        print("Num Batches: ", len(batched_sentences))

        predictions = []
        for batch in batched_sentences:
            prediction_start_time = datetime.datetime.now()
            print("".join(["Batch size:", str(len(batch))]))
            encoded = self.encoder.batch_encode_plus(batch, return_tensors='pt', pad_to_max_length=True)
            with torch.no_grad():
                batch_predictions = torch.argmax(self.model(input_ids=encoded['input_ids'], attention_mask=encoded['attention_mask'], token_type_ids=encoded['token_type_ids'])[0], dim=2).tolist()
            predictions.extend(batch_predictions)
            prediction_end_time = datetime.datetime.now()
            print("".join(["Batch time:", str(prediction_end_time - prediction_start_time)]))

        tags = []
        for prediction, tokens in zip(predictions, sents):
            prediction = self._predictions_for_tokens(tokens, [self.tag_names[index] for index in prediction[1: -1]])
            tags.append(zip(tokens, prediction))

        end_time = datetime.datetime.now()
        print("".join(["Total time for batch_tag:", str(end_time - start_time)]))

        return tags
