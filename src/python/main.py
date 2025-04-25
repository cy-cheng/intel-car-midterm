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
# MAZE_FILE = "src/python/data/t_maze.csv"
MAZE_FILE = "src/python/data/final_maze.csv"
# MAZE_FILE = "src/python/data/medium_maze.csv"
MAZE_SRC = 23
BT_PORT = "COM4"
MODE = "0"
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

    # interface.send_instruction("f")

    # return

    if mode == "0":
        log.info("Mode 0: For treasure-hunting")
        judge = ScoreboardServer(team_name, UID_FILE, server_url)

        route = path_finder.find_optimal_route()
        print(route)
        interface.send_instruction(path_finder.path(route[0]))

        deadline = time.time() + 70
        print(f"starting time: {deadline - 70}")
        print(f"deadline: {deadline}")
        judge.start_game(team_name)
        # judge.send_all(UID_FILE)

    elif mode == "1":
        log.info("Mode 1: Self-testing mode.")
        judge = ScoreboardFake(TEAM_NAME, "src/python/data/fakeUID.csv") # for local testing

        route = path_finder.find_optimal_route()
        print(route)
        interface.send_instruction(path_finder.path(route[0]))

        deadline = time.time() + 70

    sent_uid = set() 

    times_up = False

    while True:
        print(route)
        if time.time() > deadline and not times_up:
            times_up = True
            log.info("**Time is up!**")
        car_msg = interface.fetch_info()
        if car_msg == "": continue
        if len(car_msg) > 6:
            print(f"current time: {time.time()}")
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
                interface.send_instruction(path_finder.path(route[0])[1:])

            # print(f"route up: {route}")
            # print(f"current uid: {uid}")
            # print(f"current uid: {car_msg[0:8]}")
            judge.add_UID(uid)
            sent_uid.add(uid)
        elif car_msg[0] == "t":
            print(f"current time: {time.time()}")
            # print(f"We have received a t")
            path_finder.set_current_pos(route[0])
            route = path_finder.find_optimal_route()
            if len(route) > 0:
                interface.send_instruction(path_finder.path(route[0])[1:])
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
