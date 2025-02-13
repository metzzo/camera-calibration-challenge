# encoding: utf-8
"""
@author:  sherlock
@contact: sherlockliao01@gmail.com

and

@author:  davide zambrano
@contact: d.zambrano@sportradar.com


"""

from torch.utils import data

from .datasets.mnist import MNIST
from .datasets.viewds import VIEWDS
from .datasets.viewds import SVIEWDS, GenerateSViewDS
from .transforms import build_transforms

DATASETS = {"mnist": MNIST, "viewds": VIEWDS, "sviewds": SVIEWDS}


def build_dataset(cfg, transforms, is_train=True, split=None):
    """Create dataset.

    Args:
        cfg (_type_): config file
        transforms (_type_): _description_
        is_train (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    kwargs = {
        "root": "./",
        "train": is_train,
        "transform": transforms,
        "download": False,
    }
    if cfg.DATASETS.TRAIN == "sviewds":
        width, height = (
            cfg.INPUT.MULTIPLICATIVE_FACTOR * cfg.INPUT.GENERATED_VIEW_SIZE[0],
            cfg.INPUT.MULTIPLICATIVE_FACTOR * cfg.INPUT.GENERATED_VIEW_SIZE[1],
        )
        def_min, def_max = (
            cfg.INPUT.MULTIPLICATIVE_FACTOR * cfg.INPUT.GENERATED_DEF_PM[0],
            cfg.INPUT.MULTIPLICATIVE_FACTOR * cfg.INPUT.GENERATED_DEF_PM[1],
        )
        svds = GenerateSViewDS(
            output_shape=(
                width,
                height,
            ),
            def_min=def_min,
            def_max=def_max,
        )
        SPLIT = {"val": svds.val, "test": svds.test}
        if is_train:
            kwargs = {
                "vds": svds.train,
                "transform": transforms,
            }
        else:
            kwargs = {
                "vds": SPLIT[cfg.DATASETS.EVAL_ON],
                "transform": transforms,
            }
        if cfg.DATASETS.EVALUATION:
            kwargs["return_camera"] = True

    if cfg.DATASETS.TRAIN == "viewds":
        kwargs["num_elements"] = cfg.DATASETS.NUM_ELEMENTS
    datasets = DATASETS[cfg.DATASETS.TRAIN](**kwargs)
    return datasets


def make_data_loader(cfg, is_train=True):
    """Create the data loader.

    Args:
        cfg (_type_): _description_
        is_train (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    if is_train:
        batch_size = cfg.SOLVER.IMS_PER_BATCH
        shuffle = True
    else:
        batch_size = cfg.TEST.IMS_PER_BATCH
        shuffle = False

    transforms = build_transforms(cfg, is_train)
    datasets = build_dataset(cfg, transforms=transforms, is_train=is_train)
    num_workers = cfg.DATALOADER.NUM_WORKERS
    data_loader = data.DataLoader(
        datasets,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
    )

    return data_loader
