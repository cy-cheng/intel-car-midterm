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
        path_finder.set_current_pos(0)
        route = path_finder.find_optimal_route()
        interface.send_instruction(path_finder.path(route[0]))

        deadline = time.time() + 70
        judge.start_game(team_name)

        while True:
            car_msg = interface.fetch_info().split()
            if car_msg == "": continue # car_msg = [status, card_uid]

            if car_msg[0] == "e":
                interface.send_instruction(path_finder.path(route[0]))
            else:
                status, card_uid = car_msg[0], car_msg[1]
                route = path_finder.find_optimal_route(deadline - time.time())
                interface.send_instruction(path_finder.path(route[0]))

                judge.add_UID(card_uid)

    elif mode == "1":
        log.info("Mode 1: Self-testing mode.")

        # interface.start()
        # interface.send_instruction("fx")

        path_finder = Maze("src/python/data/small_maze.csv", 3)
        route = path_finder.find_optimal_route()
        print(route)
        interface.send_instruction(path_finder.path(route[0]) + "x")

        deadline = time.time() + 70
        # judge.start_game(team_name)

        sent_uid = set() 

        while True:
            car_msg = interface.fetch_info()
            if car_msg == "": continue # car_msg = [status, card_uid]
            # print("debug a")
            if len(car_msg) > 6:
                uid = car_msg[0:8]
                if uid in sent_uid:
                    print(f"Already sent {uid}, skip")
                    continue

                # print(f"current car_msg: {car_msg}")
                # print(f"current uid: {uid}")
                path_finder.set_current_pos(route[0])
                route = path_finder.find_optimal_route()
                while True:
                    car_msg = interface.fetch_info()
                    if car_msg == "": continue
                    # print("debug b")
                    if car_msg[0] == "t": break

                if len(route) > 0:
                    interface.send_instruction("b" + path_finder.path(route[0])[1:] + "x")

                # print(f"route up: {route}")
                # print(f"current uid: {uid}")
                # print(f"current uid: {car_msg[0:8]}")
                judge.add_UID(uid)
                sent_uid.add(uid)
            elif car_msg[0] == "t":
                # print(f"We have received a t")
                path_finder.set_current_pos(route[0])
                route = path_finder.find_optimal_route()
                if len(route) > 0:
                    interface.send_instruction("b" + path_finder.path(route[0])[1:] + "x")
                # print(f"route down: {route}")

                while len(car_msg) < 6:
                    car_msg = interface.fetch_info()
                # print("debug c")
                
                uid = car_msg[0:8]
                print(uid)
                judge.add_UID(uid)
                sent_uid.add(uid)
    else:
        log.error("Invalid mode")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))
