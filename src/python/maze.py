import csv
import logging
import math
import queue
from enum import IntEnum
from typing import List

import numpy as np
import pandas

from node import Direction, Node

graph = []

dir_char = ["f", "r", "b", "l"]
turn_time = [0, 1, 2, 1] # can be [0, 1, 2, 1]
dcoords = [(0, 1), (-1, 0), (0, -1), (1, 0)] # N W S E

def dtheta(s, t):
    return (t - s + 4) % 4

log = logging.getLogger(__name__)

def dijkstra(start, dis, graph, optimal_path, coords, flg = False):
    V = len(graph)
    visited = [False] * V
    for i in range(4):
        if graph[start][i][0] != -1: dir = i

    dis[start] = (0, dir)

    q = queue.PriorityQueue()
    q.put((0, start))

    while not q.empty():
        u = q.get()[1]
        visited[u] = True

        for i in range(4):
            v, d = graph[u][i]
            if v == -1 or visited[v]: continue

            new_dis = dis[u][0] + turn_time[dtheta(i, dis[u][1])] + d
            # print(f"u: {u}, v: {v}, new_dis: {new_dis}")
            if dis[v][0] > new_dis:
                if flg:
                    coords[v] = (coords[u][0] + dcoords[i][0] * d, coords[u][1] + dcoords[i][1] * d)
                dis[v] = (new_dis, i)
                optimal_path[v] = optimal_path[u] + dir_char[dtheta(i, dis[u][1])]
                q.put((dis[v][0], v))

class Maze:
    def __init__(self, file: str, start: int = 0):
        with open(file, "r") as f:
            maze = list(csv.reader(f))[1:]
            V = len(maze)

            for i in range(V):
                for j in range(len(maze[i])):
                    if maze[i][j] == "":
                        maze[i][j] = "0"
                adjacency = [(int(maze[i][j]) - 1, int(maze[i][j + 4])) for j in range(1, 5)]

                # NWSE -> 0123
                adjacency[1], adjacency[2] = adjacency[2], adjacency[1]

                graph.append(adjacency)

        # print(f"Graph: {graph}")

        self.graph = graph
        self.key_vertex = []
        for i in range(V):
            sum = 0
            for j in range(4): 
                if graph[i][j][0] != -1: sum += 1
            if sum == 1: self.key_vertex.append(i)

        self.dis = [[(325325, 0) for _ in range(V)] for _ in range(V)]
        self.optimal_path = [["" for _ in range(V)] for _ in range(V)]
        self.visited = [False for _ in range(V)]
        self.current_pos = start
        coords = [(0, 0) for _ in range(V)]

        dijkstra(start, self.dis[start], self.graph, self.optimal_path[start], coords, flg = True)

        # print(f"Start: {start}, coords: {coords[start]}")

        for u in self.key_vertex:
            if u == start: continue
            dijkstra(u, self.dis[u], self.graph, self.optimal_path[u], coords)

        self.value = [abs(coords[i][0]) + abs(coords[i][1]) for i in range(V)]

    def path(self, dest: int):
        return self.optimal_path[self.current_pos][dest]

    def print_graph(self):
        print(self.key_vertex)
        print(*self.graph, sep="\n")

    def find_optimal_route(self, time_limit: int = 70):
        id = []
        for i in self.key_vertex:
            if not self.visited[i]: id.append(i)

        V = len(id)

        score = [0 for _ in range(1 << V)]

        for u in range(V):
            score[1 << u] = self.value[id[u]]

        for msk in range(1 << V):
            score[msk] = score[msk - (msk & -msk)] + score[msk & -msk]

        time = [[325325 for _ in range(V)] for _ in range(1 << V)]
        prev_pos = [[-1 for _ in range(V)] for _ in range(1 << V)]

        max_score_msk = 0
        for i in range(V):
            time[1 << i][i] = self.dis[self.current_pos][id[i]][0]
            if score[1 << i] > score[max_score_msk] and time[1 << i][i] < time_limit:
                max_score_msk = 1 << i

        for msk in range(1 << V):
            for u in range(V):
                if (msk >> u) == 0: continue
                if time[msk][u] > time_limit: continue
                for v in range(V):
                    if (msk >> v) & 1: continue
                    new_msk = msk | (1 << v)
                    new_time = time[msk][u] + self.dis[id[u]][id[v]][0]

                    if new_time < time_limit and time[new_msk][v] > new_time:
                        time[new_msk][v] = new_time
                        prev_pos[new_msk][v] = u
                        if score[new_msk] > score[max_score_msk]:
                            max_score_msk = new_msk

        min_end = 0
        for i in range(V):
            if time[max_score_msk][i] < time[max_score_msk][min_end]:
                min_end = i

        ret = []
        while max_score_msk != 0:
            ret.append(id[min_end])
            min_end, max_score_msk = prev_pos[max_score_msk][min_end], max_score_msk & ~(1 << min_end)

        return ret[::-1]

    def set_current_pos(self, pos: int):
        self.visited[pos] = True
        self.current_pos = pos

    def mark_as_visited(self, UID_file: str):
        import csv
        with open(UID_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows[1:]:
                uid, pos = row
                pos = int(pos)
                if pos in self.key_vertex:
                    self.visited[pos] = True
                    log.info(f"Marking {uid} as visited at position {pos}")
                else:
                    log.warning(f"Invalid UID: {uid} at position {pos}")

if __name__ == "__main__":
    maze = Maze("src/python/data/cross_maze.csv", 0)
    maze.mark_as_visited("src/python/data/realUID.csv")
    maze.print_graph()

    print([(maze.value[u], u) for u in maze.key_vertex])

    exit(0)

    route = maze.find_optimal_route()

    # print(f"route: {route}")

    import time
    import random

    while True:
        time.sleep(1)

        s = time.time()
        print(maze.find_optimal_route(random.randint(0, 4000)))
        e = time.time()
        print(f"Time: {e - s:.2f} s")
        

    # while True:
    #     try:
    #         print(maze.optimal_path[maze.current_pos][route[0]])
    #     except:
    #         print("No node reachable")

    #     ans = input("Enter current status: ").split()

    #     if ans[0] == "t":
    #         maze.set_current_pos(route[0])

    #         route = maze.find_optimal_route(int(ans[1]))
    #     elif ans[0] == "e":
    #         print(route)
