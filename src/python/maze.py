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

dir_char = ["f", "l", "b", "r"]
turn_time = [0, 0, 0, 0] # can be [0, 1, 2, 1]

def dtheta(s, t):
    return (t - s + 4) % 4

log = logging.getLogger(__name__)

def dijkstra(start, dis, graph):
    V = len(graph)
    visited = [False] * V
    for i in range(4):
        if graph[start][i][0] != -1: dir = i

    dis[start] = (0, i)

    q = queue.PriorityQueue()
    q.put((0, start))

    while not q.empty():
        u = q.get()[1]
        visited[u] = True

        for i in range(4):
            v = graph[u][i][0]
            if v == -1 or visited[v]: continue

            if dis[v][0] > dis[u][0] + turn_time[dtheta(i, dis[u][1])] + graph[u][i][1]:
                dis[v] = (dis[u][0] + turn_time[dtheta(i, dis[u][1])] + graph[u][i][1], i)
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

        self.dis = [[(1000, 0) for _ in range(V)] for _ in range(V)]
        optimal_path = [["" for _ in range(V)] for _ in range(V)]

        for u in self.key_vertex:
            dijkstra(u, self.dis[u], self.graph)


    def print_graph(self):
        print(*self.graph, sep="\n")

    def find_optimal_route(self):
        pass

    def set_current_pos(self, pos: int):
        self.key_visited[pos] = True

if __name__ == "__main__":
    maze = Maze("src/python/data/small_maze.csv")