# import threading
import math
import numpy as np
from time import sleep
import copy
import itertools
from multiprocessing import Process, Lock
import random


# TODO : step need to pass AI players
# TODO: random shuffle game state when player is unaware
class State:
    class STATE_ID:
        CHOW = 0
        DISCARD = 1
        PUNG1 = 2
        PUNG2 = 3
        PUNG3 = 4
        FINISHED = 5

    def __init__(self, state_id, last_tile, players, remain_cards, idx):
        self.last_tile = last_tile
        self.players = players
        self.idx = idx
        self.state_id = state_id
        self.remain_cards = remain_cards
        self.winner = -1

    def get_action_space(self):
        if self.state_id == State.STATE_ID.CHOW:
            can_chow, sols = self.players[self.idx].can_chow(self.last_tile)
            return [None, *sols] if can_chow else [None]
        elif self.state_id == State.STATE_ID.DISCARD:
            return self.players[self.idx]._tiles
        elif State.STATE_ID.PUNG1 <= self.state_id <= State.STATE_ID.PUNG3:
            can_pung = self.players[(self.idx + 1 + self.state_id - State.STATE_ID.PUNG1) % 4].can_pung(self.last_tile)
            return [False, True] if can_pung else [False]
        elif self.state_id == State.STATE_ID.FINISHED:
            return []
        else:
            raise Exception('invalid state id')

    @staticmethod
    def step(s, a):
        sprime = copy.deepcopy(s)
        if sprime.state_id == State.STATE_ID.CHOW:
            sprime.state_id = State.STATE_ID.DISCARD
            if a is not None:
                sprime.players[sprime.idx].remove(a)
            else:
                sprime.players[sprime.idx].add(sprime.remain_cards.pop(0))
                if sprime.players[sprime.idx].respond_complete():
                    sprime.state_id = State.STATE_ID.FINISHED
                    sprime.winner = sprime.idx
        elif sprime.state_id == State.STATE_ID.DISCARD:
            sprime.last_tile = a
            sprime.players[sprime.idx].remove(a)
            sprime.state_id = State.STATE_ID.PUNG1
            for i in range(sprime.idx + 1, sprime.idx + 4):
                if sprime.players[i % 4].respond_complete(sprime.last_tile):
                    sprime.state_id = State.STATE_ID.FINISHED
                    sprime.winner = i % 4
                    break
            if len(sprime.remain_cards) == 0 and sprime.state_id != State.STATE_ID.FINISHED:
                sprime.state_id = State.STATE_ID.FINISHED
                sprime.winner = -1
        elif State.STATE_ID.PUNG1 <= sprime.state_id <= State.STATE_ID.PUNG3:
            if a:
                sprime.idx = (sprime.idx + 1 + sprime.state_id - State.STATE_ID.PUNG1) % 4
                sprime.players[sprime.idx].remove([sprime.last_tile, sprime.last_tile])
                sprime.state_id = State.STATE_ID.DISCARD
            else:
                sprime.state_id += 1
                if sprime.state_id > State.STATE_ID.PUNG3:
                    sprime.idx = (sprime.idx + 1) % 4
                    sprime.state_id = State.STATE_ID.CHOW
        return sprime


class Node:
    def __init__(self, src, state, priors=None):
        self.state = state
        self.a = state.get_action_space()
        if not priors:
            priors = np.ones([len(self.a)]) * 1. / len(self.a)
        self.src = src
        self.edges = []
        self.lock = Lock()
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
        self.lock = Lock()
        self.r = 0
        self.p = prior
        self.src = src
        self.node = None


class MCTree:
    def __init__(self, state, idx):
        self.root = Node(None, state)
        self.idx = idx
        self.counter = 0
        self.counter_lock = Lock()

    def rollout(self, node):
        state = node.state
        while state.state_id != State.STATE_ID.FINISHED:
            state = State.step(state, random.choice(state.get_action_space()))
        if state.winner == self.idx:
            r = 1
        elif state.winner >= 0:
            r = -1
        else:
            r = 0
        return r

    def search(self, nthreads, n):
        self.counter = n
        procs = []
        for i in range(nthreads):
            p = Process(target=self.search_thread, args=())
            procs.append(p)
            p.start()
            sleep(0.05)
        for p in procs:
            p.join()
        print([e.n for e in self.root.edges])

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
            # print(val)
            if leaf:
                self.backup(leaf, val)
            print([e.n for e in self.root.edges])

    def explore(self, node):
        # TODO: add virtual loss for current branch
        node.lock.acquire()
        edge = node.choose(1.)
        if edge.node:
            node.lock.release()
            if edge.terminated:
                return edge.r, edge.node
            else:
                return self.explore(edge.node)
        else:
            sprime = State.step(node.state, edge.a)
            edge.node = Node(edge, sprime)
            node.lock.release()
            if sprime.state_id == State.STATE_ID.FINISHED:
                if sprime.winner == self.idx:
                    r = 1
                elif sprime.winner >= 0:
                    r = -1
                else:
                    r = 0
                edge.terminated = True
                edge.r = r
                return r, edge.node
            return self.rollout(edge.node), edge.node

    def backup(self, node, v):
        while node.src:
            edge = node.src
            edge.lock.acquire()
            edge.n += 1
            edge.w += v
            edge.q = edge.w / edge.n
            edge.lock.release()
            node = edge.src
            assert edge in node.edges
            if node == self.root:
                print(edge.n)

    def predict(self, temp):
        # print([e.n for e in self.root.edges])
        probs = np.array([pow(e.n, 1. / temp) for e in self.root.edges])
        print([e.n for e in self.root.edges])
        probs = probs / np.sum(probs)
        # print(probs)

        return np.random.choice(self.root.a, p=probs)
