import pygame
import re
import pickle

if __name__ == '__main__':
    d = set()
    with open('AgariIndex.java') as f:
        while True:
            l = f.readline()
            if not l:
                break
            if 'tbl.put' in l:
                k = int(re.findall('0[Xx]\w+', l)[0], 0)
                d.add(k)
    with open('complete.pickle', 'wb') as f:
        pickle.dump(d, f)
    with open('complete.pickle', 'rb') as f:
        b = pickle.load(f)
        print(len(b))
