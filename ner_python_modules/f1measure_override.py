from typing import Dict, List, Optional, Set, Callable
from collections import defaultdict

import torch

from allennlp.training.metrics.metric import Metric
from allennlp.training.metrics.span_based_f1_measure import SpanBasedF1Measure as OriginalMeasure

@Metric.register("span_f1", exist_ok=True)
class SpanBasedF1Measure(OriginalMeasure):
    def get_metric(self, reset):
        """
        # Returns

        A Dict per label containing following the span based metrics:
        precision : float
        recall : float
        f1-measure : float

        Additionally, an `overall` key is included, which provides the precision,
        recall and f1-measure for all spans.
        """
        all_tags: Set[str] = set()
        all_tags.update(self._true_positives.keys())
        all_tags.update(self._false_positives.keys())
        all_tags.update(self._false_negatives.keys())
        all_metrics = {}
        for tag in all_tags:
            precision, recall, f1_measure = self._compute_metrics(
                self._true_positives[tag], self._false_positives[tag], self._false_negatives[tag]
            )
            precision_key = "precision" + "-" + tag
            recall_key = "recall" + "-" + tag
            f1_key = "f1-measure" + "-" + tag
            all_metrics[precision_key] = precision
            all_metrics[recall_key] = recall
            all_metrics[f1_key] = f1_measure

            tp_key = "tp-" + tag
            fp_key = "fp-" + tag
            fn_key = "fn-" + tag
            all_metrics[tp_key] = self._true_positives[tag]
            all_metrics[fp_key] = self._false_positives[tag]
            all_metrics[fn_key] = self._false_negatives[tag]

        # Compute the precision, recall and f1 for all spans jointly.
        precision, recall, f1_measure = self._compute_metrics(
            sum(self._true_positives.values()),
            sum(self._false_positives.values()),
            sum(self._false_negatives.values()),
        )
        all_metrics["precision-overall"] = precision
        all_metrics["recall-overall"] = recall
        all_metrics["f1-measure-overall"] = f1_measure
        if reset:
            self.reset()
        return all_metrics
