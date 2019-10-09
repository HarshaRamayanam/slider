#!/usr/bin/python3

import random
import heapq
from copy import copy, deepcopy

# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s12.html
def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    newcopy = Empty()
    newcopy.__class__ = obj.__class__
    return newcopy

# https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/
def ok_parity(n, tiles):
    n2 = len(tiles)
    inversions = 0
    blankpos = None
    for i in range(n2):
        if tiles[i] == 0:
            blankpos = i
            continue
        for j in range(i + 1, n2):
            if tiles[j] == 0:
                continue
            if tiles[j] < tiles[i]:
                inversions += 1
    if (n & 1) == 1:
        return (inversions & 1) == 0
    blankrow = blankpos // n
    return (blankrow & 1) != (inversions & 1)

class Pstate(object):
    def __init__(self, k, s):
        self.k = k
        self.s = s
    
    def __eq__(self, o):
        self.k == o.k
    
    def __lt__(self, o):
        self.k < o.k
    
    def state(self):
        return self.s

class Puzzle(object):

    def __init__(self, n, sat=True):
        tiles = [i for i in range(n**2)]
        random.shuffle(tiles)
        while sat and not ok_parity(n, tiles):
            random.shuffle(tiles)
        puzzle = []
        self.blank = None
        for i in range(n):
            row = []
            for j in range(n):
                tile = tiles[n * i + j]
                row.append(tile)
                if tile == 0:
                    self.blank = (i, j)
            puzzle.append(row)
        assert self.blank != None
        self.n = n
        self.puzzle = puzzle
        self.g = 0

    def __copy__(self):
        newcopy = empty_copy(self)
        newcopy.puzzle = deepcopy(self.puzzle)
        newcopy.n = self.n
        newcopy.blank = self.blank
        newcopy.g = self.g
        return newcopy

    def __str__(self):
        n = self.n
        result = ""
        for i in range(n):
            for j in range(n):
                tile = self.puzzle[i][j]
                if tile == 0:
                    result += "   "
                else:
                    result += "{:2} ".format(tile)
            result += "\n"
        return result
    
    def moves(self):
        n = self.n
        b = self.blank
        (i, j) = b
        ms = []
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            xi = i + d[0]
            xj = j + d[1]
            if xi >= 0 and xi < n and xj >= 0 and xj < n:
                ms.append(((xi, xj), b))
        return ms

    def move(self, m):
        assert m[1] == self.blank
        (i, j) = m[1]
        assert self.puzzle[i][j] == 0
        (xi, xj) = m[0]
        tmp = self.puzzle[xi][xj]
        self.puzzle[xi][xj] = self.puzzle[i][j]
        self.puzzle[i][j] = tmp
        self.blank = (xi, xj)

    def target(self, t):
        n = self.n
        if t == 0:
            return (n - 1, n - 1)
        i = (t - 1) // n
        j = (t - 1) - n * i
        return (i, j)

    def solved(self):
        n = self.n
        for t in range(n * n):
            (i, j) = self.target(t)
            if self.puzzle[i][j] != t:
                return False
        return True

    def solve_astar(self):
        start = copy(self)
        start.parent = None
        start.move = None
        visited = {hash(start)}
        q = []
        heapq.heappush(q, Pstate(start.g, start))
        while len(q) > 0:
            s = heapq.heappop(q).state()

            if s.solved():
                soln = []
                while True:
                    s = s.parent
                    if not s:
                        break
                    soln.append(s.move)
                return list(reversed(soln))

            ms = s.moves()
            
            for m in ms:
                c = copy(s)
                c.move(m)
                if hash(c) not in visited:
                    c.parent = s
                    c.move = m
                    c.g = s.g + 1
                    visited.add(hash(c))
                    heapq.heappush(q, Pstate(c.g, c))

        return None
            

    def __eq__(self, other):
        self.puzzle == other.puzzle
            
    def puzzle_list(self):
        result = []
        for row in self.puzzle:
            for tile in row:
                result.append(tile)
        return result

    def __hash__(self):
        return hash(tuple(self.puzzle_list()))

p = Puzzle(3)
print(p)
soln = p.solve_astar()
if soln:
    print(len(soln))
else:
    print("no solution found")
