"""analyze and visualize gait using Python from hdf5 file"""

import logging
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import pygame

pygame.display.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Gait Visualization")

PATH_TO_ASSETS = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=wrong-import-position
# pylint: disable=import-error
from logging_formatter import CustomFormatter


pygame_icon = pygame.image.load(PATH_TO_ASSETS / "shoes_icon.png")
pygame.display.set_icon(pygame_icon)

# configure logging

# create log with 'spam_application'
log = logging.getLogger("My_app")
log.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

log.addHandler(ch)

# global variables
HD5_FILE = PATH_TO_ASSETS / "MP101.hdf5"  # labelling as constant as of right now


def init() -> tuple[np.ndarray[np.real]]:
    """initialize the data from the hdf5 file

    Returns
    -------
    tuple[np.ndarray[np.real]]
        the time, left shank, left thigh, right shank, and right thigh data

    Raises
    ------
    AssertionError
        if the data is not the same length
    OSError
        if the file cannot be opened or cannot be found"""
    file: h5py.File = h5py.File(HD5_FILE, "r")

    log.debug("Keys: %s", list(file.keys()))
    print(list(file["Day_1"]["Trial_01"]))
    # print(file["Meta"]["Code"])

    time_arr: np.ndarray[np.real] = np.array(file["Day_1"]["Trial_01"]["Time"])
    log.debug("time generated with shape %s", time_arr.shape)
    left_shank: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Acc_Left_Shank"]
    )
    log.debug("left_shank generated with shape %s", left_shank.shape)
    left_thigh: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Acc_Left_Thigh"]
    )
    log.debug("left thigh generated with shape %s", left_thigh.shape)
    right_shank: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Acc_Right_Shank"]
    )
    log.debug("right shank generated with shape %s", right_shank.shape)
    right_thigh: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Acc_Right_Thigh"]
    )
    log.debug("right thigh generated with shape %s", right_thigh.shape)

    file.close()

    assert (
        time_arr.shape[0]
        == left_shank.shape[0]
        == left_thigh.shape[0]
        == right_shank.shape[0]
        == right_thigh.shape[0]
    ), "all arrays must be the same length"

    return time_arr, left_shank, left_thigh, right_shank, right_thigh


def main() -> None:
    """main function"""
    time_arr, left_shank, left_thigh, right_shank, right_thigh = init()
    i = 0
    while True:
        screen.fill((0, 0, 0))
        screen.blit(pygame_icon, (i, 0))
        for event in pygame.event.get():
            # pylint: disable-next=no-member
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(1)

        time.sleep(time_arr[i + 1] - time_arr[i])
        # refreshes screen
        pygame.display.flip()
        i += 1


if __name__ == "__main__":
    main()
