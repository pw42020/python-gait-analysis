"""reads file assets, and then sends the data as a zmq server

References
----------
Hu B, Rouse E, Hargrove L. Benchmark Datasets for Bilateral Lower-Limb
Neuromechanical Signals from Wearable Sensors during Unassisted Locomotion
in Able-Bodied Individuals. Front Robot AI. 2018 Feb 19;5:14.
doi: 10.3389/frobt.2018.00014. Erratum in: Front Robot AI. 2018 Nov 20;5:127.'
PMID: 33500901; PMCID: PMC7805660.
"""
import logging
import sys
import time
import csv
from pathlib import Path
from typing import Final

import zmq
import numpy as np

PATH_TO_ASSETS: Final[Path] = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=import-error
# pylint: disable=wrong-import-position

from logging_formatter import CustomFormatter
import shank_thigh_send_pb2 as pb  # protocol buffer python formatted library

# global variables

SAMPLES_PER_SECOND: Final[int] = 30
TOPIC: Final[str] = "LEG_DATA"

# configure logging

# create log with 'spam_application'
log = logging.getLogger("My_app")
log.setLevel(logging.INFO)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(CustomFormatter())

log.addHandler(ch)


def open_csv_file() -> dict[str, list]:
    """opens the csv file from assets containing all the data

    Returns
    -------
    dict[str, list]
        dictionary containing all the data from the csv file
    """
    return_dictionary: dict[str, list[float]] = {}
    with open(PATH_TO_ASSETS / "data.run", encoding="utf-8", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        data = list(reader)[1:]
        return_dictionary.update(
            {"LS": [[float(row[0]), float(row[1]), float(row[2])] for row in data]}
        )
        return_dictionary.update(
            {"LT": [[float(row[3]), float(row[4]), float(row[5])] for row in data]}
        )
        return_dictionary.update(
            {"RS": [[float(row[6]), float(row[7]), float(row[8])] for row in data]}
        )
        return_dictionary.update(
            {"RT": [[float(row[9]), float(row[10]), float(row[11])] for row in data]}
        )

        del data  # to get some more space
    # sio_data = sio.loadmat(PATH_TO_ASSETS / "DataShort.mat")
    # print(sio_data["DataShort"])

    return return_dictionary


def initialize_zmq_server(ip_address: str, port: int) -> tuple[zmq.Context, zmq.Socket]:
    """initialize a zmq server for sending protobuf
    data to a client"""

    ctx = zmq.Context.instance()

    url: str = f"tcp://{ip_address}:{port}"
    server = ctx.socket(zmq.PUB)
    server.bind(url)

    log.info("server bound to %s", url)

    return ctx, server


def main() -> None:
    """main function of program that takes data and then
    sends it to a client through ZMQ"""
    assert len(sys.argv) == 3
    _, server = initialize_zmq_server(ip_address=sys.argv[1], port=int(sys.argv[2]))
    leg_data: Final[dict[str, list]] = open_csv_file()

    for i in range(len(leg_data["LT"])):
        # create a protobuf message and send it to the client
        message = pb.LegData()
        message.left_thigh.x = leg_data["LT"][i][0]
        message.left_thigh.y = leg_data["LT"][i][1]
        message.left_thigh.z = leg_data["LT"][i][2]
        message.left_shank.x = leg_data["LS"][i][0]
        message.left_shank.y = leg_data["LS"][i][1]
        message.left_shank.z = leg_data["LS"][i][2]
        message.right_thigh.x = leg_data["RT"][i][0]
        message.right_thigh.y = leg_data["RT"][i][1]
        message.right_thigh.z = leg_data["RT"][i][2]
        message.right_shank.x = leg_data["RS"][i][0]
        message.right_shank.y = leg_data["RS"][i][1]
        message.right_shank.z = leg_data["RS"][i][2]

        server.send(message.SerializeToString())
        log.debug(
            "sent message %s to %s:%sunder topic %s",
            f"{TOPIC}  {message.SerializeToString()}",
            sys.argv[1],
            sys.argv[2],
            TOPIC,
        )
        time.sleep(1 / SAMPLES_PER_SECOND)
    server.close()


if __name__ == "__main__":
    main()
