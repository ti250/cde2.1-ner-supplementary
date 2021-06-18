from chemdataextractor.doc import Document, Sentence
from chemdataextractor.doc.text import RichToken

NER_TAG = "ner_tag"


def _is_divider(line: str) -> bool:
    empty_line = line.strip() == ''
    if empty_line:
        return True
    else:
        first_token = line.split()[0]
        if first_token == "-DOCSTART-":
            return True
        else:
            return False


def read_iob_dataset(file_path):
    with open(file_path) as f:
        sent = []
        for line in f:
            if _is_divider(line):
                if sent:
                    text = " ".join(sent)
                    sentence = Sentence(text)
                    tokens = []
                    for word in sent:
                        tokens.append(RichToken(text=word, start=0, end=0, lexicon=sentence.lexicon, sentence=sentence))
                    sentence._tokens = tokens
                    yield sentence
                    sent = []
            else:
                split_line = line.strip().split()
                if len(split_line) == 2:
                    sent.append(split_line[0])


def create_document_for_dataset(file_path):
    sents = [sent for sent in read_iob_dataset(file_path)]
    return Document(*sents)


def write_to(file, tokens):
    string_to_write = ""
    for token in tokens:
        tag = token[NER_TAG]
        if tag is None:
            tag = "O"
        text = token.text
        text_for_tag = text + " " + tag
        string_to_write += text_for_tag
        string_to_write += "\n"
    string_to_write += "\n\n"
    file.write(string_to_write)


def predict_document_for_dataset(file_path, output_path):
    doc = create_document_for_dataset(file_path)
    with open(output_path, 'w+') as f:
        for sent in doc.elements:
            write_to(f, sent.tokens)


if __name__ == "__main__":

    dataset_path = "DATASET_PATH"
    output_path = "CDE_PREDICTIONS_PATH"
    predict_document_for_dataset(dataset_path, output_path)
