import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import cohen_kappa_score as kappa
from sklearn.metrics import f1_score
from skmultiflow.data import DataStream

from src.core.core import Core
from src.detection.fixed_threshold import FixedThreshold
from src.detection.normal import Normal
from src.detection.statistical import Statistical
from src.reaction.exchange import Exchange
from src.reaction.pareto import Pareto
from src.ssl.ensemble import Ensemble
from src.ssl.self_flexcon import SelfFlexCon
from src.utils import Log

detectors = [Normal]
reactors = [Exchange, Pareto]

# datasets = glob('datasets/*.csv')
# datasets.sort()
datasets = [
    "Connect-4.csv",
    "Electricity.csv",
    "Fars.csv",
    "ForestCover.csv",
    "GEARS2C2D.csv",
    "Poker.csv",
    "Shuttle.csv",
    "UG2C3D.csv",
]

# statistics = "drift"
statistics = "simple"

for dataset in datasets:
    for reactor in reactors:
        for detector in detectors:
            dydasl = Core(Ensemble, detector, reactor)
            dydasl.configure_params(
                ssl_algorithm=SelfFlexCon,
                params_ssl_algorithm={},
                params_detector={},
                params_reactor={},
            )
            dydasl.add_metrics("acc", accuracy_score)
            dydasl.add_metrics("f1", f1_score)
            dydasl.add_metrics("kappa", kappa)

            dydasl.reset()
            print(dataset)
            dataframe = pd.read_csv(
                dataset if "datasets/" in dataset else "datasets/" + dataset
            )
            Log().filename = {
                "data_name": dataset.split(".", maxsplit=1)[0].split("/")[-1],
                "method_name": f"DyDaSL_{type(dydasl.detector).__name__}"
                f"_{type(dydasl.reactor).__name__}_{statistics}",
            }
            # depende do dataset
            dim = dataframe.shape
            array = dataframe.values
            instances = array[: dim[0], : dim[1] - 1]
            target = array[: dim[0], dim[1] - 1]
            class_set = np.unique(target)
            class_count = np.unique(target).shape[0]
            stream = DataStream(
                instances,
                target,
                target_idx=-1,
                n_targets=class_count,
                cat_features=None,  # Categorical features?
                name=None,
                allow_nan=True,
            )
            Log().write_archive_header()
            dydasl.run(stream, statistics)
