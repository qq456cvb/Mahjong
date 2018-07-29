import threading
from pyenv import Env
import math
import numpy as np
from time import sleep


class Node:
    def __init__(self, src, state, actions, priors):
        self.s = state
        self.a = actions
        self.src = src
        self.edges = []
        self.lock = threading.Lock()
        for i in range(self.a.size):
            self.edges.append(Edge(self, self.s, self.a[i], priors[i]))

    def choose(self, c):
        nsum_sqrt = math.sqrt(sum([e.n for e in self.edges]))
        cands = [e.q + c * e.p * nsum_sqrt / (1 + e.n) for e in self.edges]
        return self.edges[np.argmax(cands)]


class Edge:
    def __init__(self, src, state, action, prior):
        self.s = state
        self.a = action
        self.n = 0
        self.w = 0
        self.q = 0
        self.terminated = False
        self.r = 0
        self.p = prior
        self.src = src
        self.node = None


class MCTree:
    def __init__(self, env):
        self.env = env
        self.root = Node(None, )
        self.counter = 0
        self.counter_lock = threading.Lock()
        # self.evaluator = CardEvaluator


    def rollout(self, node):


    def search(self, nthreads, n):
        self.counter = n
        threads = []
        for i in range(nthreads):
            t = threading.Thread(target=self.search_thread, args=())
            threads.append(t)
            t.start()
            sleep(0.05)
        for t in threads:
            t.join()

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
        edge = node.choose(5.)
        if edge.node:
            if edge.terminated:
                node.lock.release()
                return edge.r, edge.node
            else:
                node.lock.release()
                return self.explore(edge.node)
        else:
            sprime, r, done = self.env.step_static(edge.s, edge.a, self.sess, *self.oppo_agents)
            subspace = self.env.get_actionspace(sprime)
            edge.node = Node(edge, sprime, subspace, self.agent.predict(sprime, subspace, self.sess))
            if done:
                edge.terminated = True
                edge.r = r
                node.lock.release()
                return r, edge.node
            if sprime.is_intermediate():
                node.lock.release()
                return self.explore(edge.node)
            node.lock.release()
            return self.agent.evaluate(sprime, self.sess), edge.node

    def backup(self, node, v):
        while node.src:
            node.lock.acquire()
            edge = node.src
            edge.n += 1
            edge.w += v
            edge.q = edge.w / edge.n
            node.lock.release()
            node = edge.src
