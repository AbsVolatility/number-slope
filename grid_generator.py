import random
from itertools import groupby

import sys
import time

class ContradictionError(Exception):
    pass

class Node:
    def __init__(self, row, col, tile):
        self.row = row
        self.col = col
        self.tile = tile
        self.value = 0
        self.possible = True


def tile_grid(n):
    """Try to generate a random tiling of an n-by-n square using n n-ominoes.
    Return False if the generation fails."""
    grid = [[0]*n for _ in xrange(n)]
    for i in xrange(1, n+1):
        for row_num, row in enumerate(grid):
            if 0 in row:
                col = row.index(0)
                row = row_num
                break
        grid[row][col] = i
        adjacent = []
        for _ in xrange(n-1):
            if row != 0 and not grid[row-1][col] and (row-1, col) not in adjacent:
                adjacent.append((row-1, col))
            if row != n-1 and not grid[row+1][col] and (row+1, col) not in adjacent:
                adjacent.append((row+1, col))
            if col != 0 and not grid[row][col-1] and (row, col-1) not in adjacent:
                adjacent.append((row, col-1))
            if col != n-1 and not grid[row][col+1] and (row, col+1) not in adjacent:
                adjacent.append((row, col+1))
            try:
                row, col = random.choice(adjacent)
            except IndexError:
                return False
            adjacent.remove((row, col))
            grid[row][col] = i
    return grid


def find_possible(rows, cols, tiles, runs, i):
    """Find the nodes which could possibly have the value i, given a grid.
    Operates in-place."""
    for row in rows:
        for node in row:
            node.possible = not node.value
        if any(node.value == i for node in row):
            for node in row:
                node.possible = False
    for col in cols:
        if any(node.value == i for node in col):
            for node in col:
                node.possible = False
    for tile in tiles:
        if any(node.value == i for node in tile):
            for node in tile:
                node.possible = False
    for tile_runs in runs:
        for run in tile_runs:
            if all(node.value == 0 for node in run):
                for node in run[1:-1]:
                    node.possible = False
            else:
                if run[0].value == 0:
                    run = run[::-1]
                try:
                    for node in run[next(idx for idx, ele in enumerate(run) if ele.value == 0)+1:]:
                        node.possible = False
                except StopIteration:
                    pass


def update_possible(rows, cols, tiles, filled_node):
    """Update the nodes which could possibly have the value i, given a grid and a filled-in node.
    Operates in-place."""
    for node in rows[filled_node.row]:
        node.possible = False
    for node in cols[filled_node.col]:
        node.possible = False
    for node in tiles[filled_node.tile]:
        node.possible = False


def fill_grid(rows, cols, tiles, runs, n):
    moves = []
    i = 1
    num_filled = 0
    while i <= n:
        find_possible(rows, cols, tiles, runs, i)
        try:
            while True:
                updated = False
                for row in rows + cols:
                    if any(node.value == i for node in row):
                        continue
                    possible = [node for node in row if node.possible]
                    if not possible:
                        raise ContradictionError
                    if len(possible) == 1:
                        node = possible[0]
                        node.value = i
                        num_filled += 1
                        moves.append(node)
                        update_possible(rows, cols, tiles, node)
                        updated = True
                    elif len(set(node.tile for node in possible)) == 1:
                        for node in tiles[possible[0].tile]:
                            if node not in possible and node.possible:
                                node.possible = False
                                updated = True
                for tile in tiles:
                    if any(node.value == i for node in tile):
                        continue
                    possible = [node for node in tile if node.possible]
                    if not possible:
                        raise ContradictionError
                    if len(possible) == 1:
                        node = possible[0]
                        node.value = i
                        num_filled += 1
                        moves.append(node)
                        update_possible(rows, cols, tiles, node)
                        updated = True
                    elif len(set(node.row for node in possible)) == 1:
                        for node in rows[possible[0].row]:
                            if node not in possible and node.possible:
                                node.possible = False
                                updated = True
                    elif len(set(node.col for node in possible)) == 1:
                        for node in cols[possible[0].col]:
                            if node not in possible and node.possible:
                                node.possible = False
                                updated = True
                    elif len(possible) == 2:
                        node1, node2 = possible
                        node3 = rows[node1.row][node2.col]
                        node4 = rows[node2.row][node1.col]
                        if node3.possible:
                            node3.possible = False
                            updated = True
                        if node4.possible:
                            node4.possible = False
                            updated = True
                if not updated:
                    if num_filled == n:
                        i += 1
                        num_filled = 0
                        break
                    for tile in tiles:
                        possible = [node for node in tile if node.possible]
                        if possible:
                            node = possible.pop(0)
                            moves.append(possible)
                            node.value = i
                            num_filled += 1
                            moves.append(node)
                            update_possible(rows, cols, tiles, node)
                            break
        except ContradictionError:
            while True:
                try:
                    node = moves.pop()
                    node.value = 0
                    if num_filled:
                        num_filled -= 1
                    else:
                        num_filled = n-1
                        i -= 1
                except IndexError:  # moves list is empty, no possible filling
                    return False
                except AttributeError:  # pop a list
                    guess = node.pop(0)
                    if node:
                        moves.append(node)
                    guess.value = i
                    num_filled += 1
                    moves.append(guess)
    return rows


def generate_grid(n):
    """Try to fill a random tiling of an n-by-n square using n n-ominoes."""
    while True:
        grid = tile_grid(n)
        if grid:
            break
    rows = [tuple(Node(row_num, col_num, tile_num-1) for col_num, tile_num in enumerate(row))
            for row_num, row in enumerate(grid)]
    cols = zip(*rows)
    tiles = [[] for _ in xrange(n)]
    for node in sum(rows, ()):
        tiles[node.tile].append(node)
    runs = [[] for _ in xrange(n)]
    for row in rows + cols:
        for tile_num, run in groupby(row, key=lambda node_:node_.tile):
            run = list(run)
            if len(run) > 1:
                runs[tile_num].append(run)
    return fill_grid(rows, cols, tiles, runs, n)


n = int(sys.argv[1])
tries = 0
start_time = time.time()
while True:
    tries += 1
    grid = generate_grid(n)
    if grid:
        break
    if tries % 1000 == 0:
        print tries, "tries"
time_taken = time.time() - start_time
print "\n".join(["".join([str(node.tile) for node in row]) for row in grid])
print
print "\n".join(["".join([str(node.value) for node in row]) for row in grid])
print
print tries, "tries"
print "Completed in", int(time_taken), "seconds"


"""
n = 9
tries = 0
start_time = time.time()
for _ in xrange(100):
    while True:
        tries += 1
        grid = tile_grid(n)
        if grid:
            break
time_taken = time.time() - start_time
print round(tries/100.0, 2), "tries on average"
print "Completed in", time_taken/100, "seconds on average"
"""

"""
n = 9
start_time = time.time()
for _ in xrange(50):
    grid = generate_grid(n)
    if grid:
        print "\n".join(["".join([str(node.tile) for node in row]) for row in grid])
        print
        print "\n".join(["".join([str(node.value) for node in row]) for row in grid])
        print
time_taken = time.time() - start_time
print "Completed in", time_taken/50, "seconds on average"
"""