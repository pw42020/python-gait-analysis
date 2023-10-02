"""analyze and visualize gait using Python from hdf5 file

https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10063557/#CR9

Another link that may be usedful for a database of gait data

Note: I'm going to guess that I provide the initial angles and data for
the position of everything and then the program will calculate the rest"""

import logging
import sys
import time
import csv
from enum import Enum, auto
from typing import Final
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R
import scipy.io as sio
import pygame


class LegSide(Enum):
    """the type of data that is being used"""

    LEFT: Final[int] = auto()
    RIGHT: Final[int] = auto()


# global variables

WIDTH: Final[int] = 640
HEIGHT: Final[int] = 480

# leg stuff
LENGTH: Final[int] = 70  # length from shaft to knee or thigh to knee
LEG_TO_CENTER: Final[int] = 10  # distance from center of leg to center of screen
DEFAULT_LEG_POSITIONS: Final[dict[str, tuple[int, int]]] = {
    "LS": (WIDTH / 2 - LEG_TO_CENTER, HEIGHT / 2 + LENGTH),
    "RS": (WIDTH / 2 + LEG_TO_CENTER, HEIGHT / 2 + LENGTH),
    "LT": (WIDTH / 2 - LEG_TO_CENTER, HEIGHT / 2 - LENGTH),
    "RT": (WIDTH / 2 + LEG_TO_CENTER, HEIGHT / 2 - LENGTH),
}

SAMPLES_PER_SECOND: Final[int] = 500


pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gait Visualization")


PATH_TO_ASSETS = Path(__file__).parent.parent.parent / "assets"
PATH_TO_ORIENTATION_DATA = PATH_TO_ASSETS / "P15"
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


def init() -> dict[str, np.ndarray[float]]:
    """initialize the program"""
    return_dictionary: dict[str, np.ndarray[float]] = {}
    with open(PATH_TO_ASSETS / "leg_data.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        data = list(reader)[1:]
        return_dictionary.update(
            {"RS": [[float(row[0]), float(row[1]), float(row[2])] for row in data]}
        )
        return_dictionary.update(
            {"RT": [[float(row[6]), float(row[7]), float(row[8])] for row in data]}
        )
        return_dictionary.update(
            {"LS": [[float(row[12]), float(row[13]), float(row[14])] for row in data]}
        )
        return_dictionary.update(
            {"LT": [[float(row[18]), float(row[19]), float(row[20])] for row in data]}
        )

        del data  # to get some more space
    # sio_data = sio.loadmat(PATH_TO_ASSETS / "DataShort.mat")
    # print(sio_data["DataShort"])

    return return_dictionary


def get_knee_pos(
    thigh: tuple[float, float],
    thigh_pitch: np.ndarray[float],
    legside: LegSide,
) -> tuple[np.ndarray[np.real]]:
    """getting the knee position based on the shank and thigh

    Parameters
    ----------
    shank : np.ndarray[np.real]
        the shank data
    thigh : np.ndarray[np.real]
        the thigh data"""

    return (
        thigh[0] - LENGTH * np.sin(thigh_pitch[0]),
        thigh[1] + LENGTH * np.cos(thigh_pitch[0]),
    )


def convert_quat_to_euler(quat: np.ndarray[np.real]) -> np.ndarray[np.real]:
    """convert a quaternion to euler angles

    Parameters
    ----------
    quat : np.ndarray[np.real]
        the quaternion to convert

    Returns
    -------
    np.ndarray[np.real]
        the euler angles of the quaternion"""

    euler_angles = R.from_quat(quat).as_euler("xyz", degrees=True)

    log.debug("euler angles: %s", euler_angles)
    return euler_angles


def get_thigh_pos(data: np.ndarray[np.real], legside: LegSide) -> tuple[np.real]:
    """get the coordinates of the thigh

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

    return DEFAULT_LEG_POSITIONS["LT" if legside == LegSide.LEFT else "RT"]


def get_shank_pos(
    shank_data: np.ndarray[np.real], knee_pos: tuple[float, float], legside: LegSide
) -> tuple[np.real]:
    """get the coordinates of the thigh

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

    ret_tuple = (
        knee_pos[0] + LENGTH * np.sin(shank_data[2]),
        knee_pos[1] + LENGTH * np.cos(shank_data[2]),
    )
    log.debug("ret_tuple: %s", ret_tuple)
    return ret_tuple


def main() -> None:
    """main function"""
    leg_data: Final[dict[str, np.ndarray[np.real]]] = init()
    i = 1422

    while i != len(leg_data["LS"]) - 1:
        screen.fill((0, 0, 0))

        l_thigh = get_thigh_pos(data=leg_data["LT"][i], legside=LegSide.LEFT)
        l_knee = get_knee_pos(
            thigh=l_thigh,
            thigh_pitch=leg_data["LT"][i],
            legside=LegSide.LEFT,
        )
        l_shank = get_shank_pos(
            shank_data=leg_data["LS"][i],
            knee_pos=l_knee,
            legside=LegSide.LEFT,
        )

        log.debug("l_thigh: %s", l_thigh)
        log.debug("l_knee: %s", l_knee)
        log.debug("l_shank: %s", l_shank)

        # create line from shank to knee and knee to thigh
        pygame.draw.line(screen, (255, 255, 255), l_shank, l_knee)
        pygame.draw.line(screen, (255, 255, 255), l_knee, l_thigh)

        r_thigh = get_thigh_pos(data=leg_data["RT"][i], legside=LegSide.RIGHT)
        r_knee = get_knee_pos(
            thigh=r_thigh,
            thigh_pitch=leg_data["RT"][i],  # convert_quat_to_euler(leg_data["RT"][i])
            legside=LegSide.RIGHT,
        )
        r_shank = get_shank_pos(
            shank_data=leg_data["RS"][i],
            knee_pos=r_knee,
            legside=LegSide.RIGHT,
        )

        log.debug("r_thigh: %s", r_thigh)
        log.debug("r_knee: %s", r_knee)
        log.debug("r_shank: %s", r_shank)

        # create line from shank to knee and knee to thigh
        pygame.draw.line(screen, (255, 255, 255), r_shank, r_knee)
        pygame.draw.line(screen, (255, 255, 255), r_knee, r_thigh)

        pygame.draw.line(screen, (255, 255, 255), l_thigh, r_thigh)

        for event in pygame.event.get():
            # pylint: disable-next=no-member
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(1)

        time.sleep(1 / SAMPLES_PER_SECOND)
        # refreshes screen
        pygame.display.flip()
        i += 1


if __name__ == "__main__":
    main()
