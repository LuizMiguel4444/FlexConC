from numpy import ndarray
from skmultiflow.trees import HoeffdingTreeClassifier as HT

from src.reaction.interfaces.ireaction import IReaction
from src.ssl.ensemble import Ensemble


class Exchange(IReaction):
    """Módulo de reação ao drift por troca de classificador"""
    def __init__(self, **params):
        self.classifier = params.get("classifier") or HT

    def react(
        self,
        ensemble: Ensemble,
        instances: ndarray,
        labels: ndarray,
        thr: float,
        retrain_classifier: bool = True,
    ) -> Ensemble:
        y_pred_classifier = ensemble.measure_ensemble(instances, labels)
        pos = [p for p, acc in enumerate(y_pred_classifier) if acc < thr]
        ensemble.swap(
            [self.classifier()],
            pos,
            instances,
            labels,
            retrain_classifier
        )

        return ensemble
