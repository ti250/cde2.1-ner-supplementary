import copy
from collections import namedtuple


class F1Score(object):

    def __init__(self, classes=[]):
        common_dict = {}
        for class_ in classes:
            common_dict[class_] = 0
        self.true_positives = copy.copy(common_dict)
        self.true_negatives = copy.copy(common_dict)
        self.false_positives = copy.copy(common_dict)
        self.false_negatives = copy.copy(common_dict)
        self.classes = classes

    def update_score_from_spans(self, true_spans, predicted_spans):
        # Spans should be a namedtuple with name, start, and end

        for span in predicted_spans:
            if span in true_spans:
                self.true_positives[span.name] += 1
                true_spans.remove(span)
            else:
                self.false_positives[span.name] += 1

        for span in true_spans:
            self.false_negatives[span.name] += 1

    def precision(self, class_):
        tp = self.true_positives[class_]
        fp = self.false_positives[class_]
        if tp + fp == 0:
            return None
        return tp / (tp + fp)

    def recall(self, class_):
        tp = self.true_positives[class_]
        fn = self.false_negatives[class_]
        if tp + fn == 0:
            return None
        return tp / (tp + fn)

    def f1_score(self, class_):
        precision = self.precision(class_)
        recall = self.recall(class_)
        if precision is None or recall is None:
            return None
        return 2 * (precision * recall) / (precision + recall)

    def total_true_positives(self):
        total = 0
        for class_ in self.classes:
            total += self.true_positives[class_]
        return total

    def total_true_negatives(self):
        total = 0
        for class_ in self.classes:
            total += self.true_negatives[class_]
        return total

    def total_false_negatives(self):
        total = 0
        for class_ in self.classes:
            total += self.false_negatives[class_]
        return total

    def total_false_positives(self):
        total = 0
        for class_ in self.classes:
            total += self.false_positives[class_]
        return total

    def total_precision(self):
        tp = self.total_true_positives()
        fp = self.total_false_positives()
        if tp + fp == 0:
            return None
        return tp / (tp + fp)

    def total_recall(self):
        tp = self.total_true_positives()
        fn = self.total_false_negatives()
        if tp + fn == 0:
            return None
        return tp / (tp + fn)

    def total_f1_score(self):
        precision = self.total_precision()
        recall = self.total_recall()
        if precision is None or recall is None:
            return None
        return 2 * (precision * recall) / (precision + recall)

    def __str__(self):
        return self.printable_form()

    def printable_form(self):
        total_string_rep = ""
        class_string_rep = "{class_}: TP: {tp}, FP: {fp}, TN: {tn}, FN:{fn}\n -Precision:{precision}\n -Recall:{recall}\n -F1:{f1}"
        for class_ in self.classes:
            precision = self.precision(class_)
            recall = self.recall(class_)
            f1_score = self.f1_score(class_)
            class_string = class_string_rep.format(class_=class_,
                                                   tp=self.true_positives[class_],
                                                   fp=self.false_positives[class_],
                                                   tn=self.true_negatives[class_],
                                                   fn=self.false_negatives[class_],
                                                   precision=precision,
                                                   recall=recall,
                                                   f1=f1_score,
                                                  )
            total_string_rep += (class_string + "\n")
        total_precision = self.total_precision()
        total_recall = self.total_recall()
        total_f1 = self.total_f1_score()
        total_string_rep += "\n-------------------------------------------------------------------\n"
        overall_string = class_string_rep.format(class_="Total",
                                               tp=self.total_true_positives(),
                                               fp=self.total_false_positives(),
                                               tn=self.total_true_negatives(),
                                               fn=self.total_false_negatives(),
                                               precision=total_precision,
                                               recall=total_recall,
                                               f1=total_f1,
                                              )
        total_string_rep += overall_string
        return total_string_rep


