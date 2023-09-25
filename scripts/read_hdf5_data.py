"""break hdf5 data down into understandable informaiton"""
import sys
from pathlib import Path
import logging

import numpy as np
import h5py
import pygame

PATH_TO_ASSETS = Path(__file__).parent.parent / "assets"
HD5_FILE = PATH_TO_ASSETS / "MP101.hdf5"  # labelling as constant as of right now

sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=wrong-import-position
# pylint: disable=import-error
from logging_formatter import CustomFormatter  # noqa: E402


# configure logging

# create log with 'spam_application'
log = logging.getLogger("My_app")
log.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

log.addHandler(ch)


if __name__ == "__main__":
    with h5py.File(HD5_FILE, "r") as f:
        log.debug("Keys: %s", list(f.keys()))
        print(list(f["Day_1"]["Trial_01"]))
        # print(f["Meta"]["Code"])

        time: np.ndarray[np.real] = np.array(f["Day_1"]["Trial_01"]["Time"])
        log.debug("%s", time.shape)
        left_shank: np.ndarray[np.real] = np.array(
            f["Day_1"]["Trial_01"]["Acc_Left_Shank"]
        )
        log.debug("%s", left_shank.shape)
        left_thigh: np.ndarray[np.real] = np.array(
            f["Day_1"]["Trial_01"]["Acc_Left_Thigh"]
        )
        log.debug("%s", left_thigh.shape)
        right_shank: np.ndarray[np.real] = np.array(
            f["Day_1"]["Trial_01"]["Acc_Right_Shank"]
        )
        log.debug("%s", right_shank.shape)
        right_thigh: np.ndarray[np.real] = np.array(
            f["Day_1"]["Trial_01"]["Acc_Right_Thigh"]
        )
        log.debug("%s", right_thigh.shape)

        assert (
            time.shape[0]
            == left_shank.shape[0]
            == left_thigh.shape[0]
            == right_shank.shape[0]
            == right_thigh.shape[0]
        ), "all arrays must be the same length"
