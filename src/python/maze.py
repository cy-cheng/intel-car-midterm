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
turn_time = [0, 0, 0, 0] # can be [0, 1, 2, 1]
dcoords = [(0, 1), (-1, 0), (0, -1), (1, 0)] # N W S E

def dtheta(s, t):
    return (t - s + 4) % 4

log = logging.getLogger(__name__)

def dijkstra(start, dis, graph, optimal_path, coords):
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
            if dis[v][0] > new_dis:
                coords[v] = (coords[u][0] + dcoords[i][0], coords[u][1] + dcoords[i][1])
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
        self.current_pos = 0
        coords = [(0, 0) for _ in range(V)]

        for u in self.key_vertex:
            dijkstra(u, self.dis[u], self.graph, self.optimal_path[u], coords)

        self.value = [abs(coords[i][0]) + abs(coords[i][1]) for i in range(V)]

    def print_graph(self):
        print(*self.graph, sep="\n")

    def find_optimal_route(self, time_limit: int = 70):
        id = []
        for i in self.key_vertex:
            if not self.visited[i]: id.append(i)

        V = len(id)

        score = [0 for _ in range(1 << V)]

        for i in range(V):
            score[1 << i] = 1

        for msk in range(1 << V):
            score[msk] = score[msk - (msk & -msk)] + score[msk & -msk]

        time = [[325325 for _ in range(V)] for _ in range(1 << V)]
        route = [[[] for _ in range(V)] for _ in range(1 << V)]

        max_score_msk = 0
        for i in range(V):
            time[1 << i][i] = self.dis[self.current_pos][id[i]][0]
            route[1 << i][i] = [i]
            if score[1 << i] > score[max_score_msk]:
                max_score_msk = 1 << i

        for msk in range(1 << V):
            for u in range(V):
                if (msk >> u) == 0: continue
                if time[msk][u] > time_limit: continue
                for v in range(V):
                    if (msk >> v) & 1: continue
                    new_msk = msk | (1 << v)
                    new_time = time[msk][u] + self.dis[id[u]][id[v]][0]

                    if time[new_msk][v] > new_time:
                        time[new_msk][v] = new_time
                        route[new_msk][v] = route[msk][u] + [v]
                        if score[new_msk] > score[max_score_msk]:
                            max_score_msk = new_msk

        min_end = 0
        for i in range(V):
            if time[max_score_msk][i] < time[max_score_msk][min_end]:
                min_end = i

        return [id[u] for u in route[max_score_msk][min_end]]


    def set_current_pos(self, pos: int):
        self.visited[pos] = True
        self.current_pos = pos

if __name__ == "__main__":
    maze = Maze("src/python/data/small_maze.csv")

    print(maze.find_optimal_route())