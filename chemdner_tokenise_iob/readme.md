# Tokenizing the CHEMDNER files

The CHEMDNER files are given in an untokenized manner, which can be a problem when training certain NER models. These scripts convert the CHEMDNER files into something that is in the CONLL 2003 format. 

The `chemdner_process_with_cde.py` file should be edited to process CHEMDNER files in this manner using ChemDataExtractor. Most of the parameters should be self explanatory, but there are a few to keep note of. Firstly, by changing the `word_tokenizer`, one can play around with different tokenizers, whether those included with ChemDataExtractor or those developed elsewhere. 

Secondly, the `lenient` parameter controls what happens should an NER span crosses only part of a token. For example, take a tokenizer that would regard `blood-oxygen-level` as one token. `oxygen` is a chemical entity, but the rest isn't. If `lenient` is set to `True`, this is partially ignored and the whole token is regarded as a chemical entity. On the other hand, if `lenient` is set to `False`, this is regarded as a different type of token, a partial chemical entity. 
When creating a tokenized dataset for training, we recommend setting `lenient` to `True` as the model should never predict partial chemical entities, while when evaluating, we recommend setting it to `False` so that any tokenization errors are counted as something wrong when evaluating.

The `test_alt_tokenizers.py` script calculates some statistics based off which tokenizers can be compared. The CHEMDNER dataset should be processed using each tokenizer, and the outputs should be placed into some directory with the name of the file being the name of the tokenizer + .txt. 

Further analysis can also be performed using `test_distribution_sent_lengths.py`, which also plots the distribution of sentence lengths in terms of tokens when tokenized using certain tokenizers. Some examples of the output can be found in the Supplementary Information.
