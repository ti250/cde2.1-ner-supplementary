# NER Evaluation scripts

Included in this folder are a number of scripts to make NER evaluation with ChemDataExtractor much easier.

`cde_predictions_on_iob.py` takes the path to an IOB tokenised file (such as those made using the files in `chemdner_tokenise_iob`) in `dataset_path` and uses ChemDataExtractor to perform Named Entity Recognition on it, the result of which is saved in `output_path`.

The file created from this can be fed into `evaluate_datasets.py`, as `predicted_file_loc`, along with the original annotated file (produced using the scripts from `chemdner_tokenise_iob`), and prints out the F1 Score and other statistics.
