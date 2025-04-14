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
MAZE_FILE = "src/python/data/small_maze.csv"
BT_PORT = "COM7"
MODE = "1"


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
    maze = Maze(maze_file)
    # judge = ScoreboardServer(team_name, server_url)
    judge = ScoreboardFake(TEAM_NAME, "src/python/data/fakeUID.csv") # for local testing
    interface = BTInterface(port=bt_port)

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        # TODO : for treasure-hunting, which encourages you to hunt as many scores as possible

        path_finder = Maze("src/python/data/small_maze.csv")

        while True:
            car_msg = interface.bt.serial_read_string()



    elif mode == "1":
        log.info("Mode 1: Self-testing mode.")

        # interface.start()
        interface.bt.serial_write_string("flbrx")

        path_finder = Maze("src/python/data/small_maze.csv")

        print(maze.find_optimal_route())

        while True:
            str = interface.bt.serial_read_string()

            if str != "":
                print(str)
                log.info("Received: %s", str)

                # next_path = path_finder.find_optimal_route()
                # interface.bt.serial_write_string(next_path)

            interface.bt.serial_write_string(input("Enter next path: "))

                # pos, id = str.split(" ")
                # judge.add_UID(id)
                # pathFinder.set_current_pos(pos)

                # interface.bt.serial_write_string(pathFinder.nextTarget())

    else:
        log.error("Invalid mode")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
