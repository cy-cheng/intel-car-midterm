import argparse
import logging
import os
import sys
import time

import numpy as np
import pandas
from BTinterface import BTInterface
from maze import Maze
from score import ScoreboardServer, ScoreboardFake

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

# TODO : Fill in the following information
TEAM_NAME = "我爸是 MVP"
SERVER_URL = "http://140.112.175.18:5000/"
# MAZE_FILE = "src/python/data/cross_maze.csv"
# MAZE_FILE = "src/python/data/t_maze.csv"
MAZE_FILE = "src/python/data/medium_maze.csv"
MAZE_SRC = 0
BT_PORT = "COM4"
MODE = "1"
UID_FILE = "src/python/data/realUID.csv"
slow_speed_set = {
    "adj1": 30,
    "adj2": 100,
    "adj3": 60,
    "avel": 250,
    "bvel": 250,
    "slow": 600,
    "back_slow": 350,
    "magic_sec": 150,
}

SPEED_SET = slow_speed_set

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=MODE, help="0: treasure-hunting, 1: self-testing", type=str)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()


def main(mode: int, bt_port: str, team_name: str, server_url: str, maze_file: str):
    path_finder = Maze(maze_file, MAZE_SRC)
    path_finder.print_graph()
    # path_finder.mark_as_visited(UID_FILE)
    inst = " ".join([str(value) for value in SPEED_SET.values()])
    print(inst)
    # judge = ScoreboardServer(team_name, UID_FILE, server_url)
    # judge.send_all(UID_FILE)
    interface = BTInterface(port=bt_port)

    #     interface.send_instruction(str(value))
    #     car_msg = interface.fetch_info()
    # for i in range(9):
    #     while car_msg == "":
    #         car_msg = interface.fetch_info()

    while True:
        s = input("input: ")
        interface.send_instruction(s)

        car_msg = interface.bt.serial_read_string()

        while car_msg == "":
            car_msg = interface.bt.serial_read_string()

        print(car_msg)

        # car_msg = interface.fetch_info()

        # while car_msg == "":
            # car_msg = interface.fetch_info()

    else:
        log.error("Invalid mode")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
