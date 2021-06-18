# Assume text and annotations in same order in terms of PID

from collections import namedtuple

ChemdnerData = namedtuple("ChemdnerData", ["pmid", "title", "abstract"])
Annotation = namedtuple("Annotation", ["start", "end", "text"])
AnnotatedChemdnerData = namedtuple("AnnotatedChemdnerData", ["text", "annotation"])


def read_chemdner_text(file_location):
    with open(file_location) as f:
        for line in f:
            split_line = line.split("\t")
            yield ChemdnerData(split_line[0], split_line[1], split_line[2])


def read_chemdner_annotations(file_location):
    previous_id = None
    abstract_annotations = []
    title_annotations = []

    with open(file_location) as f:
        for line in f:
            split_line = line.split("\t")
            id = split_line[0]
            section = split_line[1]
            annotation = Annotation(int(split_line[2]), int(split_line[3]), split_line[4])
            if id != previous_id:
                if previous_id is not None:
                    yield ChemdnerData(previous_id, title_annotations, abstract_annotations)
                previous_id = id
                abstract_annotations = []
                title_annotations = []
            annotations_list = abstract_annotations if section == "A" else title_annotations
            annotations_list.append(annotation)
        yield ChemdnerData(previous_id, title_annotations, abstract_annotations)


def get_text_with_annotation(text_location, annotations_location):
    texts = read_chemdner_text(text_location)
    annotations = read_chemdner_annotations(annotations_location)
    annotation = ChemdnerData("-10", "", "")
    annotation_pmid = -10
    # concerned_pmid = "22288603"
    annotations_dict = {}
    for text in texts:
        if int(text.pmid) in annotations_dict.keys():
            annotation = annotations_dict[int(text.pmid)]
        else:
            while annotation_pmid < int(text.pmid):
                # pmid = annotation_pmid
                # print(text.pmid, annotation_pmid)
                annotation = next(annotations)
                annotations_dict[int(annotation.pmid)] = annotation
                annotation_pmid = int(annotation.pmid)
        annotation_current = annotation
        if str(annotation_current.pmid) != text.pmid:
            # print("creating empty for:", text.pmid, annotation_current.pmid)
            annotation_current = ChemdnerData(text.pmid, [], [])
        yield AnnotatedChemdnerData(text, annotation_current)
