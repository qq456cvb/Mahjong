import threading
import math
import numpy as np
from time import sleep
import copy
import itertools
import random


class Node:
    def __init__(self, src, env, a_type, actions, priors):
        self.env = env
        self.a_type = a_type
        self.a = actions
        self.src = src
        self.edges = []
        self.lock = threading.Lock()
        for i in range(len(self.a)):
            self.edges.append(Edge(self, self.a[i], priors[i]))

    def choose(self, c):
        nsum_sqrt = math.sqrt(sum([e.n for e in self.edges]))
        cands = [e.q + c * e.p * nsum_sqrt / (1 + e.n) for e in self.edges]
        return self.edges[np.argmax(cands)]


class Edge:
    def __init__(self, src, action, prior):
        self.a = action
        self.n = 0
        self.w = 0
        self.q = 0
        self.terminated = False
        self.r = 0
        self.p = prior
        self.src = src
        self.node = None


def clone_env(env):
    env_clone = copy.copy(env)
    env_clone._current_turn = env._current_turn
    for i in range(4):
        env_clone._players[i] = copy.deepcopy(env._players[i])
    env_clone._last_tile = env._last_tile
    env_clone._control_player = env._control_player
    env_clone._all_tiles = env._all_tiles.copy()
    env._run, env_clone._run = itertools.tee(env._run)
    env_clone._run = env_clone.run()
    env_clone._searching = env._searching
    return env_clone


class MCTree:
    def __init__(self, env, idx, a_type):
        self.idx = idx
        self.env = env
        action_space = env.get_action_space(idx, a_type)
        self.root = Node(None, env, a_type, action_space, np.ones([len(action_space)]) * 1. / len(action_space))
        self.counter = 0
        self.counter_lock = threading.Lock()

    def rollout(self, node):
        player = node.env._players[self.idx]
        player.respond_normal = lambda: player.remove(random.choice(player._tiles))

        def foo(tile):
            can_chow, sols = player.can_chow(tile)
            if can_chow:
                player.remove(random.choice(sols))
                return True
            return False
        player.respond_chow = foo

        def foo(tile):
            if player.can_pung(tile):
                player.remove([tile, tile])
                return True
            return False
        player.respond_pung = foo

        try:
            while True:
                next(node.env._run_search)
        except StopIteration as e:
            winner = e.value[0]
            if winner == self.idx:
                return 1
            elif winner == -1:
                return 0
            else:
                return -1

    def search(self, nthreads, n):
        self.counter = n
        self.env._searching = True
        threads = []
        for i in range(nthreads):
            t = threading.Thread(target=self.search_thread, args=())
            threads.append(t)
            t.start()
            sleep(0.05)
        for t in threads:
            t.join()
        self.env._searching = False

    def search_thread(self):
        while True:
            self.counter_lock.acquire()
            if self.counter == 0:
                self.counter_lock.release()
                break
            else:
                self.counter -= 1
            self.counter_lock.release()
            val, leaf = self.explore(self.root)
            if leaf:
                self.backup(leaf, val)

    def explore(self, node):
        # TODO: add virtual loss for current branch
        node.lock.acquire()
        edge = node.choose(1.)
        if edge.node:
            if edge.terminated:
                node.lock.release()
                return edge.r, edge.node
            else:
                node.lock.release()
                return self.explore(edge.node)
        else:
            env_clone = clone_env(node.env)
            print(node.env._run)
            print(env_clone._run)
            r, done, a_type = env_clone.step(self.idx, node.a_type, edge.a)
            action_space = env_clone.get_action_space(self.idx, a_type)
            edge.node = Node(edge, env_clone, a_type, action_space, np.ones([len(action_space)]) * 1. / len(action_space))
            if done:
                edge.terminated = True
                edge.r = r
                node.lock.release()
                return r, edge.node
            node.lock.release()
            return self.rollout(edge.node), edge.node

    def backup(self, node, v):
        while node.src:
            node.lock.acquire()
            edge = node.src
            edge.n += 1
            edge.w += v
            edge.q = edge.w / edge.n
            node.lock.release()
            node = edge.src

    def predict(self, temp):
        # print([e.n for e in self.root.edges])
        probs = np.array([pow(e.n, 1. / temp) for e in self.root.edges])
        probs = probs / np.sum(probs)
        # print(probs)
        return self.root.a[np.argmax(probs)]
