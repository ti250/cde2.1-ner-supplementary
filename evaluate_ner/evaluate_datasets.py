from f1_score import F1Score
from collections import namedtuple
import itertools
import json

Span = namedtuple("Span", ["name", "start", "end"])


def compare_datasets(true_data, predicted_data, classes):
    f1_score = F1Score(classes=classes)
    for true_spans, predicted_spans in zip(true_data, predicted_data):
        f1_score.update_score_from_spans(true_spans, predicted_spans)
    print(f1_score.printable_form())


def iob_to_spans(iob_sent, ignore_tags=None, replace_tags=None):
    # IOB_sent is a list of IOB tags
    spans = []
    iob_sent.append("O")
    iob_cleaned_sent = iob_sent
    if ignore_tags:
        iob_cleaned_sent = []
        for tag in iob_sent:
            if tag[2:] in ignore_tags:
                iob_cleaned_sent.append("O")
            else:
                iob_cleaned_sent.append(tag)
    if replace_tags:
        iob_sent = iob_cleaned_sent
        iob_cleaned_sent = []
        for tag in iob_sent:
            if tag[2:] in replace_tags.keys():
                tag_to_append = tag[:2] + replace_tags[tag[2:]]
                iob_cleaned_sent.append(tag_to_append)
            else:
                iob_cleaned_sent.append(tag)

    unmatched_tag_found = False
    span_start = 0
    prev_tag = "O"
    for index, tag in enumerate(iob_cleaned_sent):
        if len(prev_tag) != 0 and (prev_tag[0] == "I" or prev_tag[0] == "B"):
            if tag[0] == "I" and prev_tag[2:] != tag[2:]:
                # Case of malformed tags
                span = Span(name=prev_tag[2:], start=span_start, end=index)
                spans.append(span)
                span_start = index
                unmatched_tag_found = True
            elif len(tag) == 0 or tag[0] == "O" or tag[0] == "B":
                span = Span(name=prev_tag[2:], start=span_start, end=index)
                spans.append(span)
        if len(tag) != 0 and tag[0] == "B":
            span_start = index
        prev_tag = tag

    interested_spans = []
    interested_spans = [Span(name='MAT', start=11, end=44)]
    for span in spans:
        if span in interested_spans:
            print(iob_sent, spans)
            break

    if unmatched_tag_found:
        print(iob_sent, spans)
        print(len(iob_sent))

    return spans


def _is_divider(line):
    empty_line = line.strip() == ''
    if empty_line:
        return True
    else:
        first_token = line.split()[0]
        if first_token == "-DOCSTART-":
            return True
        else:
            return False


def read_iob_dataset(file_path, ignore_tags=None, replace_tags=None):
    with open(file_path) as f:
        for is_divider, lines in itertools.groupby(f, _is_divider):
                if not is_divider:
                    sent = [line.strip().split() for line in lines]
                    tags = []
                    for word in sent:
                        if len(word) == 2:
                            tags.append(word[-1])
                    yield iob_to_spans(tags, ignore_tags=ignore_tags, replace_tags=replace_tags)


def read_allennlp_predict_output(file_path, ignore_tags=None):
    with open(file_path) as f:
        for line in f:
            sent_dict = json.loads(line)
            sent = sent_dict["tags"]
            for tag in sent:
                if not tag[0] in ["B", "I", "O"]:
                    print("UNRECOGNISED TAG", tag)
            yield iob_to_spans(sent, ignore_tags)


if __name__ == "__main__":
    file_loc = "ANNOTATED_FILE_PATH"
    predicted_file_loc = "PREDICTED_FILE_PATH"

    replace_tags = {"CM": "CEM"}
    dataset_true = read_iob_dataset(file_loc, replace_tags=replace_tags)
    dataset_labelled = read_iob_dataset(predicted_file_loc, replace_tags=replace_tags)

    chemdner_labels = ["CEM", "PCEM"]
    labels = chemdner_labels
    compare_datasets(dataset_true, dataset_labelled, labels)
