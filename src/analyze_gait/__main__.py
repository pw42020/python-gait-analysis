"""analyze and visualize gait using Python from hdf5 file

https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10063557/#CR9

Another link that may be usedful for a database of gait data"""

import logging
import sys
import time
from typing import Final
from pathlib import Path

import h5py
import numpy as np
import pygame

# global variables

WIDTH: Final[int] = 640
HEIGHT: Final[int] = 480
LENGTH: Final[int] = 50


pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

    # get right and left knee
    right_knee: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Ang_Right_Knee"]
    )
    log.debug("right knee generated with shape %s", right_knee.shape)

    left_knee: np.ndarray[np.real] = np.array(
        file["Day_1"]["Trial_01"]["Ang_Left_Knee"]
    )
    log.debug("left knee generated with shape %s", left_knee.shape)

    file.close()

    assert (
        time_arr.shape[0]
        == left_shank.shape[0]
        == left_thigh.shape[0]
        == right_shank.shape[0]
        == right_thigh.shape[0]
        == left_knee.shape[0]
        == right_knee.shape[0]
    ), "all arrays must be the same length"

    return (
        time_arr,
        left_shank,
        left_thigh,
        right_shank,
        right_thigh,
        left_knee,
        right_knee,
    )


def get_knee_pos(
    shank: np.ndarray[np.real], thigh: np.ndarray[np.real]
) -> tuple[np.ndarray[np.real]]:
    """getting the knee position based on the shank and thigh

    Parameters
    ----------
    shank : np.ndarray[np.real]
        the shank data
    thigh : np.ndarray[np.real]
        the thigh data"""

    log.debug("shank position: %s", shank)
    log.debug("thigh position: %s", thigh)

    d_shank_thigh: np.real = np.sqrt(
        np.power(shank[0] - thigh[0], 2) + np.power(shank[1] - thigh[1], 2)
    )

    log.debug("distance between shank and thigh: %s", d_shank_thigh)

    # now new triangle has thigh at (0,0) and shank at (d_shank_thigh, 0)
    # and knee at (x, y)
    # (x^2) + y^2 = LENGTH^2
    # (x-d_shank_thigh)^2 + y^2 = LENGTH^2
    # x^2 - 2xd_shank_thigh + d_shank_thigh^2 + y^2 = LENGTH^2
    # x = d_shank_thigh^2/(2*d_shank_thigh)
    # y = sqrt(LENGTH^2 - x^2)
    x: np.real = np.power(d_shank_thigh, 2) / (2 * d_shank_thigh)
    y: np.real = np.sqrt(np.power(LENGTH, 2) - np.power(x, 2))

    # bring x and y back into their respective place
    x += thigh[0]
    y += thigh[1]

    # rotate triangle back into place
    # theta: np.real = np.arctan((shank[1] - thigh[1]) / (shank[0] - thigh[0]))

    # x = x * np.cos(theta) - y * np.sin(theta)
    # y = x * np.sin(theta) + y * np.cos(theta)

    log.debug("knee position: %s", (x, y))

    return (x, y)


def get_coordinates(data: np.ndarray[np.real]) -> tuple[np.real]:
    """get the coordinates of the data

    Parameters
    ----------
    data : np.ndarray[np.real]
        the data to get the coordinates of

    Returns
    -------
    tuple[np.real]
        the coordinates of the data

    Notes
    -----
    The coordinates are centered meaning that at (0, 0) the coordinates will
    be in the middle of the screen"""

    x: np.real = data[0] * LENGTH / 4 + WIDTH / 2
    y: np.real = data[1] * LENGTH / 4 + HEIGHT / 2

    log.info("coordinates for data: %s", (x, y))

    return (x, y)


def main() -> None:
    """main function"""
    (
        time_arr,
        left_shank,
        left_thigh,
        right_shank,
        right_thigh,
        left_knee,
        right_knee,
    ) = init()
    i = 0
    return
    while True:
        print(i)
        screen.fill((0, 0, 0))
        # for 2d knee angle, only the Y andZ coordinates are required
        l_shank_pos = get_coordinates(left_shank[i])
        l_thigh_pos = get_coordinates(left_thigh[i])
        l_knee_pos = get_knee_pos(l_shank_pos, l_thigh_pos)

        # create two lines for shank -> knee and knee -> thigh
        pygame.draw.line(screen, (255, 255, 255), l_shank_pos, l_knee_pos, 1)
        pygame.draw.line(screen, (255, 255, 255), l_knee_pos, l_thigh_pos, 1)

        # for 2d knee angle, only the Y andZ coordinates are required
        DEFAULT_LEG_DIFF: Final[
            int
        ] = 50  # difference between legs in starting position
        r_shank_pos = get_coordinates(left_shank[i])
        r_shank_pos = (r_shank_pos[0] + DEFAULT_LEG_DIFF, r_shank_pos[1])

        r_thigh_pos = get_coordinates(left_thigh[i])
        r_thigh_pos = (r_thigh_pos[0] + DEFAULT_LEG_DIFF, r_thigh_pos[1])

        r_knee_pos = get_knee_pos(r_shank_pos, r_thigh_pos)

        # create two lines for shank -> knee and knee -> thigh
        pygame.draw.line(screen, (0, 255, 0), r_shank_pos, r_knee_pos, 1)
        pygame.draw.line(screen, (0, 255, 0), r_knee_pos, r_thigh_pos, 1)

        for event in pygame.event.get():
            # pylint: disable-next=no-member
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(1)

        time.sleep(time_arr[i + 1] - time_arr[i])
        # refreshes screen
        pygame.display.flip()
        if i < time_arr.shape[0] - 2:
            i += 1
        else:
            i = 0


if __name__ == "__main__":
    main()
