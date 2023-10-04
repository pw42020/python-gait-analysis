<div align="center">
<img src="https://img.shields.io/badge/code%20style-black-000000.svg">
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54">
<img src="https://img.shields.io/badge/linting%20-pylint-FFD700.svg">
</div>

## Python Gait Analysis Module
By Liam Beguhn, Rosaha Cho, Alexander Tollman, Patrick Walsh

<div align="center">
<img src="./assets/Leg_moving.gif">
</div>

Initial Python scripted module for analyzing gait from a large dataset from Benchmark Datasets for Bilateral Lower-Limb Neuromechanical Signals from Wearable Sensors during Unassisted Locomotion in Able-Bodied Individuals.

If curious about the exacts of the data and the study, the link to the study is available [here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7805660/).

### Installation
Make sure you have [Docker](https://docs.docker.com/engine/install/) installed before attempting to recreate this code. It is required to build the containers and run the files.

For Linux and MacOS, you may have to install [ZeroMQ](https://zeromq.org/download/) separately (Windows Users please use WSL and follow the same instructions). Follow the instructions to install.

Once Docker  and ZeroMQ are installed, make sure that you download [this .zip file containing Raw and Processed leg data](https://figshare.com/ndownloader/files/10011298), take out one of the `.csv` files from the `Raw` data section, and add to the `assets/` folder in the repository.

Once the file has been added, change the name to `leg_data.csv` and you have everything properly installed and ready to go.

### Usage
For usage, simply type:
```sh
docker compose up; docker compose down
```

to execute.

Once the application has run its course, or you are done watching the application, hit `Ctrl+C` on your keyboard. The containers will stop running and will remove themselves from your computer.

> **Note**: In case you don't see the application, and you receive some information that says, `Authorization required, but no authorization protocol specified`, then look at [this StackOverflow problem](https://stackoverflow.com/questions/48833451/no-protocol-specified-when-running-a-sudo-su-app-on-ubuntu-linux) and it should yield your solution.

