"""analyze and visualize gait using Python from hdf5 file

References
----------
Hu B, Rouse E, Hargrove L. Benchmark Datasets for Bilateral Lower-Limb
Neuromechanical Signals from Wearable Sensors during Unassisted Locomotion
in Able-Bodied Individuals. Front Robot AI. 2018 Feb 19;5:14.
doi: 10.3389/frobt.2018.00014. Erratum in: Front Robot AI. 2018 Nov 20;5:127.'
PMID: 33500901; PMCID: PMC7805660.

Another link that may be usedful for a database of gait data

Note: I'm going to guess that I provide the initial angles and data for
the position of everything and then the program will calculate the rest"""

import logging
import sys
import time
from typing import Optional
from enum import Enum, auto
from typing import Final
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R
import pygame
import zmq

PATH_TO_ASSETS = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=wrong-import-position
# pylint: disable=import-error
from logging_formatter import CustomFormatter
import shank_thigh_send_pb2 as pb  # protocol buffer python formatted library


class LegSide(Enum):
    """the type of data that is being used"""

    LEFT: Final[int] = auto()
    RIGHT: Final[int] = auto()


# global variables

WIDTH: Final[int] = 640
HEIGHT: Final[int] = 480

TOPIC: Final[str] = "LEG_DATA"

# leg stuff
LENGTH: Final[int] = 70  # length from shaft to knee or thigh to knee
LEG_TO_CENTER: Final[int] = 10  # distance from center of leg to center of screen
DEFAULT_LEG_POSITIONS: Final[dict[str, tuple[int, int]]] = {
    "LS": (WIDTH / 2 - LEG_TO_CENTER, HEIGHT / 2 + LENGTH),
    "RS": (WIDTH / 2 + LEG_TO_CENTER, HEIGHT / 2 + LENGTH),
    "LT": (WIDTH / 2 - LEG_TO_CENTER, HEIGHT / 2 - LENGTH),
    "RT": (WIDTH / 2 + LEG_TO_CENTER, HEIGHT / 2 - LENGTH),
}

SAMPLES_PER_SECOND: Final[int] = 30


pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gait Visualization")


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


def get_shank_pos(
    shank_data: np.ndarray[np.real], knee_pos: tuple[float, float]
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


def initialize_zmq_client(ip_address: str, port: int) -> tuple[zmq.Context, zmq.Socket]:
    """initialize pub/sub zmq client

    Parameters
    ----------
    ip_address : str
        the ip address to connect to
    port : int
        the port to connect to"""

    ctx = zmq.Context.instance()

    url: str = f"tcp://{ip_address}:{port}"
    socket = ctx.socket(zmq.SUB)
    socket.connect(url)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.RCVTIMEO, 1000)

    log.info("client connected to %s", url)

    return ctx, socket


def main() -> None:
    """main function"""
    _, socket = initialize_zmq_client(ip_address=sys.argv[1], port=int(sys.argv[2]))
    i = 1422
    socket.subscribe("")

    while True:
        message: Optional[bytes] = None
        try:
            message = socket.recv()
            # assert message_topic == TOPIC
            leg_data = pb.LegData()
            leg_data.ParseFromString(message)

            log.debug("leg_data: %s", leg_data)
        except zmq.error.Again:
            log.error("Client timed out")
            break
        screen.fill((0, 0, 0))

        l_thigh = DEFAULT_LEG_POSITIONS["LT"]
        l_knee = get_knee_pos(
            thigh=l_thigh,
            thigh_pitch=[
                leg_data.left_thigh.x,
                leg_data.left_thigh.y,
                leg_data.left_thigh.z,
            ],
            legside=LegSide.LEFT,
        )
        l_shank = get_shank_pos(
            shank_data=[
                leg_data.left_shank.x,
                leg_data.left_shank.y,
                leg_data.left_shank.z,
            ],
            knee_pos=l_knee,
        )

        log.debug("l_thigh: %s", l_thigh)
        log.debug("l_knee: %s", l_knee)
        log.debug("l_shank: %s", l_shank)

        # create line from shank to knee and knee to thigh
        pygame.draw.line(screen, (255, 255, 255), l_shank, l_knee)
        pygame.draw.line(screen, (255, 255, 255), l_knee, l_thigh)

        r_thigh = DEFAULT_LEG_POSITIONS["RT"]
        r_knee = get_knee_pos(
            thigh=r_thigh,
            thigh_pitch=[
                leg_data.right_thigh.x,
                leg_data.right_thigh.y,
                leg_data.right_thigh.z,
            ],
            legside=LegSide.RIGHT,
        )
        r_shank = get_shank_pos(
            shank_data=[
                leg_data.right_shank.x,
                leg_data.right_shank.y,
                leg_data.right_shank.z,
            ],
            knee_pos=r_knee,
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

    socket.unsubscribe(TOPIC)
    socket.close()


if __name__ == "__main__":
    main()
