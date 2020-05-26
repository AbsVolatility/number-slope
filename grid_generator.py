import random
from itertools import groupby

import sys
import time

if sys.version_info[0] == 3:
    xrange = range
    raw_input = input


class ContradictionError(Exception):
    pass


class Node:
    def __init__(self, row, col, tile):
        self.row = row
        self.col = col
        self.tile = tile
        self.value = 0
        self.possible = True


def is_pinch_point(grid, row, col, n):
    filled = (row == 0 or bool(grid[row-1][col]))
    num_switches = 0
    for i,j in [(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]:
        next_cell = ((row+i == -1) or (row+i == n) or (col+j == -1) or (col+j == n) or bool(grid[row+i][col+j]))
        if next_cell != filled:
            num_switches += 1
        filled = next_cell
    return num_switches > 2


def tile_grid(n):
    """Try to generate a random tiling of an n-by-n square using n n-ominoes.
    Return False if the generation fails."""
    tries = 1
    grid = [[0]*n for _ in xrange(n)]
    for i in xrange(1, n):
        for row_num, row in enumerate(grid):
            possible_starts = [row[col] == 0 and not is_pinch_point(grid, row_num, col, n) for col in xrange(n)]
            if any(possible_starts):
                col = possible_starts.index(True)
                row = row_num
                break
        else:
            return False
        
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
                random.shuffle(adjacent)
                while True:
                    row, col = adjacent.pop()
                    if is_pinch_point(grid, row, col, n):
                        continue
                    break
            except IndexError:
                return False
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
                            random.shuffle(possible)
                            node = possible.pop()
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
                    guess = node.pop()
                    if node:
                        moves.append(node)
                    guess.value = i
                    num_filled += 1
                    moves.append(guess)
                    if num_filled == n:
                        i += 1
                        num_filled = 0
                    break
    return rows


def generate_grid(n):
    """Try to fill a random tiling of an n-by-n square using n n-ominoes."""
    while True:
        grid = tile_grid(n)
        if grid:
            break
    rows = [tuple(Node(row_num, col_num, tile_num) for col_num, tile_num in enumerate(row))
            for row_num, row in enumerate(grid)]
    cols = list(zip(*rows))
    tiles = [[] for _ in xrange(n)]
    for node in sum(rows, ()):
        tiles[node.tile].append(node)
    runs = [[] for _ in xrange(n)]
    for row in rows + cols:
        for tile_num, run in groupby(row, key=lambda node_:node_.tile):
            run = list(run)
            if len(run) > 2:
                runs[tile_num].append(run)
    return fill_grid(rows, cols, tiles, runs, n)


def display_grid(grid):
    """Display a completed grid."""
    n = len(grid)
    tiling = [[None]*(n+2)] + [[None] + [node.tile for node in row] + [None] for row in grid] + [[None]*(n+2)]
    pipes = [[False]*(n+1) for _ in xrange(n)]  # position of '|' characters
    for row_num, row in enumerate(tiling[1:-1]):
        i = 0
        while i <= n:
            if row[i] != row[i+1]:
                pipes[row_num][i] = True
            i += 1
    pipes_cols = list(zip(*pipes))
    tiling = list(zip(*tiling))
    dashes = [[False]*(n+1) for _ in xrange(n)]  # position of "---" characters
    for row_num, row in enumerate(tiling[1:-1]):
        i = 0
        while i <= n:
            if row[i] != row[i+1]:
                dashes[row_num][i] = True
            i += 1
    dashes = list(zip(*dashes))
    crosses = [[' ']*(n+1) for _ in xrange(n+1)]  # position of "+" characters
    for i in xrange(n+1):
        for j in xrange(n+1):
            adj_dashes = dashes[i][(j-1 if j else 0):j+1]
            adj_pipes = pipes_cols[j][(i-1 if i else 0):i+1]
            if True in adj_dashes and True in adj_pipes:
                crosses[i][j] = '+'
            elif True in adj_dashes:
                crosses[i][j] = '-'
            elif True in adj_pipes:
                crosses[i][j] = '|'
    print("")
    for row_num in xrange(n+1):
        print("{}".join(crosses[row_num]).format(*((' -'[dash])*3 for dash in dashes[row_num])))
        if row_num < n:
            print("{: ^3}".join([' |'[pipe] for pipe in pipes[row_num]]).format(*(node.value for node in grid[row_num])))


def display_tiling(grid):
    """Display a completed tiling."""
    n = len(grid)
    tiling = [[None]*(n+2)] + [[None] + [tile for tile in row] + [None] for row in grid] + [[None]*(n+2)]
    pipes = [[False]*(n+1) for _ in xrange(n)]  # position of '|' characters
    for row_num, row in enumerate(tiling[1:-1]):
        i = 0
        while i <= n:
            if row[i] != row[i+1]:
                pipes[row_num][i] = True
            i += 1
    pipes_cols = list(zip(*pipes))
    tiling = list(zip(*tiling))
    dashes = [[False]*(n+1) for _ in xrange(n)]  # position of "---" characters
    for row_num, row in enumerate(tiling[1:-1]):
        i = 0
        while i <= n:
            if row[i] != row[i+1]:
                dashes[row_num][i] = True
            i += 1
    dashes = list(zip(*dashes))
    crosses = [[' ']*(n+1) for _ in xrange(n+1)]  # position of "+" characters
    for i in xrange(n+1):
        for j in xrange(n+1):
            adj_dashes = dashes[i][(j-1 if j else 0):j+1]
            adj_pipes = pipes_cols[j][(i-1 if i else 0):i+1]
            if True in adj_dashes and True in adj_pipes:
                crosses[i][j] = '+'
            elif True in adj_dashes:
                crosses[i][j] = '-'
            elif True in adj_pipes:
                crosses[i][j] = '|'
    print("")
    for row_num in xrange(n+1):
        print("{}".join(crosses[row_num]).format(*((' -'[dash])*3 for dash in dashes[row_num])))
        if row_num < n:
            print("   ".join([' |'[pipe] for pipe in pipes[row_num]]))


try:
    n = int(sys.argv[1])
except IndexError:
    n = int(raw_input("Enter a value for n: "))

if len(sys.argv) == 2:
    tries = 0
    start_time = time.time()
    while True:
        tries += 1
        grid = generate_grid(n)
        if grid:
            break
        if tries % 500 == 0:
            print("{} tries".format(tries))
    time_taken = time.time() - start_time
    display_grid(grid)
    print("")
    print("{} tries".format(tries))
    print("Completed in {} seconds".format(int(time_taken)))

elif sys.argv[2] == "-tile":
    while True:
        grid = tile_grid(n)
        if grid:
            break
    display_tiling(grid)
    print("")
    
elif sys.argv[2] == "-g":
    try:
        N = int(sys.argv[3])
    except IndexError:
        N = 1
    attempts = []
    start_time = time.time()
    for _ in xrange(N):
        tries = 0
        while True:
            tries += 1
            grid = generate_grid(n)
            if grid:
                break
        attempts.append(tries)
    time_taken = time.time() - start_time
    print("")
    print(N, "attempts conducted")
    print("Minimum number of tries:", min(attempts))
    print("Maximum number of tries:", max(attempts))
    print("Average number of tries:", sum(attempts)/N)
    print("Completed in {:.5f} seconds".format(time_taken))
    print("")

elif sys.argv[2] == "-t":
    try:
        N = int(sys.argv[3])
    except IndexError:
        N = 100
    attempts = []
    start_time = time.time()
    for _ in xrange(N):
        tries = 0
        while True:
            tries += 1
            grid = tile_grid(n)
            if grid:
                break
        attempts.append(tries)
    time_taken = time.time() - start_time
    print("")
    print(N, "attempts conducted")
    print("Minimum number of tries:", min(attempts))
    print("Maximum number of tries:", max(attempts))
    print("Average number of tries:", sum(attempts)/N)
    print("Completed in {:.5f} seconds".format(time_taken))
    print("")


# deprecated code
def tile_grid_depr(n):
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


def generate_grid_depr(n):
    """Try to fill a random tiling of an n-by-n square using n n-ominoes."""
    while True:
        grid = tile_grid(n)
        if grid:
            break
    rows = [tuple(Node(row_num, col_num, tile_num-1) for col_num, tile_num in enumerate(row))
            for row_num, row in enumerate(grid)]
    cols = list(zip(*rows))
    tiles = [[] for _ in xrange(n)]
    for node in sum(rows, ()):
        tiles[node.tile].append(node)
    runs = [[] for _ in xrange(n)]
    for row in rows + cols:
        for tile_num, run in groupby(row, key=lambda node_:node_.tile):
            run = list(run)
            if len(run) > 2:
                runs[tile_num].append(run)
    return fill_grid(rows, cols, tiles, runs, n)