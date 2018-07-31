import pygame
import re
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, './build')
# from clib import State, TileType

if __name__ == '__main__':
    a = np.random.rand(1000)
    plt.plot(a)
    plt.show()
    b = a
    for i in range(100):
        b = np.convolve(b, a)
        b /= np.sum(b)
    plt.plot(b)
    plt.show()
    # t = TileType.BAMBOO_ONE
    # s = State(0, 0, [t], 0)
    # d = set()
    # with open('AgariIndex.java') as f:
    #     while True:
    #         l = f.readline()
    #         if not l:
    #             break
    #         if 'tbl.put' in l:
    #             k = int(re.findall('0[Xx]\w+', l)[0], 0)
    #             d.add(k)
    # with open('complete.pickle', 'wb') as f:
    #     pickle.dump(d, f)
    # with open('complete.pickle', 'rb') as f:
    #     b = pickle.load(f)
    #     print(len(b))
