from chemdataextractor.nlp.tokenize import SpacyTokenizer, ChemTokWordTokenizer, WordTokenizer, FineWordTokenizer, ChemWordTokenizer, BertWordTokenizer
from chemdataextractor.doc.text import Paragraph
from chemdner_process_with_cde import convert_chemdner_to_iob
from mpi_utils import parallelise_func
import re
import datetime


def count_occurences(pattern, file_name):
    line_count = 0
    with open(file_name) as origin_file:
        for line in origin_file:
            line = re.findall(pattern, line)
            if line:
                line_count += 1
    return line_count


def tokenizer_tester(text_location, annotations_location, root_directory):
    hyphen_pattern = re.compile(r"^\-")
    partial_pattern = re.compile(r"PCEM")
    template_string = "{file_name}:\n -Single Hyphens: {hyphen_count}\n -Partial CEMS: {partial_count} \n -Time taken: {time_taken}"

    @parallelise_func
    def test_tokenizer(tokenizer):
        before_time = datetime.datetime.now()
        print("\nAnalyzing for ", type(tokenizer).__name__)
        write_name = root_directory + str(type(tokenizer).__name__) + ".txt"
        Paragraph.word_tokenizer = tokenizer
        convert_chemdner_to_iob(text_location, annotations_location, write_name, lenient=False)
        after_time = datetime.datetime.now()
        string_to_print = template_string.format(file_name=str(type(tokenizer).__name__),
                                                 hyphen_count=str(count_occurences(hyphen_pattern, write_name)),
                                                 partial_count=str(count_occurences(partial_pattern, write_name)),
                                                 time_taken=str(after_time - before_time)
                                                 )
        print(string_to_print)

    return test_tokenizer


if __name__ == "__main__":
    tokenizers_to_test = [BertWordTokenizer(), ChemTokWordTokenizer(), SpacyTokenizer(), FineWordTokenizer(), ChemWordTokenizer(), WordTokenizer()]
    tester = tokenizer_tester(root_directory="DIRECTORY WHERE ALL THE DIFFERENTLY TOKENIZED CHEMDNER DATASETS ARE PLACED",
                             text_location="PATH TO THE TEXT FOR THE ORIGINAL CHEMDNER DATASET",
                             annotations_location="PATH TO THE ANNOTATIONS FOR THE ORIGINAL CHEMDNER DATASET")
    tester(tokenizers_to_test)
