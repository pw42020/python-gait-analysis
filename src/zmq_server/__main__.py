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

PATH_TO_ASSETS: Final[Path] = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

from logging_formatter import CustomFormatter
import shank_thigh_send_pb2 as pb  # protocol buffer python formatted library

# global variables

SAMPLES_PER_SECOND: Final[int] = 500
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


def initialize_zmq_server(ip_address: str, port: int) -> tuple[zmq.Context, zmq.Socket]:
    """initialize a zmq server for sending protobuf
    data to a client"""

    ctx = zmq.Context.instance()

    url: str = f"tcp://{ip_address}:{port}"
    server = ctx.socket(zmq.PUB)
    server.bind(url)

    log.info("server bound to %s", url)

    return ctx, server


if __name__ == "__main__":
    assert len(sys.argv) == 3
    ctx, server = initialize_zmq_server(ip_address=sys.argv[1], port=int(sys.argv[2]))
    leg_data: Final[dict[str, list]] = open_csv_file()

    for i in range(len(leg_data["LT"])):
        """create a protobuf message and send it to the client"""
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

        server.send_string(f"{TOPIC} {message.SerializeToString()}")
        log.debug(f"sent message to {sys.argv[1]}:{sys.argv[2]} under topic {TOPIC}")
        time.sleep(1 / SAMPLES_PER_SECOND)
    server.close()
