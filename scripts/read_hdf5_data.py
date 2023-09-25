"""break hdf5 data down into understandable informaiton"""
from pathlib import Path
import h5py

PATH_TO_ASSETS = Path(__file__).parent.parent / "assets"
HD5_FILE = PATH_TO_ASSETS / "MP101.hdf5"  # labelling as constant as of right now

if __name__ == "__main__":
    """configure"""
    with h5py.File(HD5_FILE, "r") as f:
        print(list(f["Day_1"]))
        print(f["Meta"]["Code"])
