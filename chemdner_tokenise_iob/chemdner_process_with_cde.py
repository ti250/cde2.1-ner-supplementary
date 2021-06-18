from tokenise_files import get_text_with_annotation
from chemdataextractor.nlp.tokenize import _SpacyTokenizer, _ChemTokWordTokenizer, WordTokenizer, FineWordTokenizer, ChemWordTokenizer, BertWordTokenizer
from chemdataextractor.doc.text import Paragraph
import sys
import re


number_pattern = re.compile('(-?\d+\.?(?:\d+)?)')
number_string = "<nUm>"


class Spinner:

    def __init__(self, interval):
        self.interval = interval
        self.cursor = ["Working.", "Working..", "Working..."]
        self.iteration = 0

    def print_spinner(self):
        if self.iteration % self.interval == 0:
            sys.stdout.write("\033[K")
            print(self.cursor[self.iteration % 3], end="\r", flush=True)
        self.iteration += 1


spinner = Spinner(10)


def create_iob_annotations(text, annotations, default_annotation, lenient=False):
    paragraph = Paragraph(text)
    for sentence in paragraph.sentences:
        for token in sentence.rich_tokens:
            token.annotation = default_annotation
    for annotation in annotations:
        for sentence in paragraph.sentences:
            if annotation.start >= sentence.start and annotation.start <= sentence.end:
                annotate_sentence(sentence, annotation, lenient)
                break
    return paragraph.sentences


def annotate_sentence(sentence, annotation, lenient=False):
    rich_tokens = sentence.rich_tokens
    adjusted_start = annotation.start
    adjusted_end = annotation.end
    for token in rich_tokens:
        current_annotation = token.annotation
        start_in_token_condition = (adjusted_start > token.start and adjusted_start < token.end)
        end_in_token_condition = (adjusted_end > token.start and adjusted_end < token.end)
        if token.start >= adjusted_start and token.end <= adjusted_end:
            current_annotation = "B-CEM"
            # print(token, annotation)
            if adjusted_start < token.start:
                current_annotation = "I-CEM"
        elif not lenient and (start_in_token_condition or end_in_token_condition):
            current_annotation = "B-PCEM"
            # print(sentence.rich_tokens, annotation, token.start < adjusted_end)
        elif start_in_token_condition:
            current_annotation = "B-CEM"
        elif end_in_token_condition:
            current_annotation = "I-CEM"
        token.annotation = current_annotation
        if token.end >= adjusted_end:
            break
    concerned_list = []
    if annotation.text in concerned_list:
        print(annotation)
        for token in rich_tokens:
            if token.text in ["TCS", "Drought", "+", "Drought+TCS"]:
                print(token, token.start, token.end, token.annotation)


def write_iob_annotations(labelled_text, output_file):
    for sentence in labelled_text:
        string_to_write = ""
        for token in sentence.rich_tokens:
            tag = token.annotation
            if tag is None:
                tag = "O"
            text_for_tag = process_token(token)
            string_to_write += text_for_tag
            string_to_write += "\n"
        string_to_write += "\n\n"
        output_file.write(string_to_write)


def process_token(token):
    tag = token.annotation
    text = token.text
    if re.fullmatch(number_pattern, text):
        text = number_string
    return text + " " + tag


def convert_chemdner_to_iob(text_location,
                            annotations_location,
                            output_location,
                            word_tokenizer
                            default_annotation="O",
                            lenient=False):
    Paragraph.word_tokenizer = word_tokenizer
    print(output_location)
    with open(output_location, "w+") as output_file:
        for element in get_text_with_annotation(text_location, annotations_location):
            spinner.print_spinner()
            text = element.text
            annotation = element.annotation
            write_iob_annotations(create_iob_annotations(text.title,
                                                         annotation.title,
                                                         default_annotation, lenient=lenient),
                                  output_file)
            write_iob_annotations(create_iob_annotations(text.abstract,
                                                         annotation.abstract,
                                                         default_annotation, lenient=lenient),
                                  output_file)


if __name__ == '__main__':
    lenient = False
    word_tokenizer = BertWordTokenizer()

    output_location = "OUTPUT FILE LOCATION"
    text_location = "PATH TO CHEMDNER TEXT"
    annotations_location = "PATH TO CHEMDNER ANNOTATIONS"
    convert_chemdner_to_iob(text_location,
                            annotations_location,
                            output_location,
                            word_tokenizer, lenient=lenient)
