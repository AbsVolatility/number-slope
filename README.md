# number-slope
Grid generator for the Number Slope logic puzzle

The program takes an argument *n*, which gives the size of the grid. E.g. on Windows, type

    python grid_generator.py 6

in the command window to get a 6x6 grid.

The program will output two grids: the first gives the *n*-omino tiling, with a number for each tile; the second gives the actual numbers. It will also give an update every 1000 tries, until it finds a solution or you force-quit the program.

**Warning**: Don't expect to get a result any time soon for *n* larger than 8.

---

The Number Slope logic puzzle (also called *Sukobai*), was first proposed on [Puzzling.StackExchange](http://puzzling.stackexchange.com/questions/47723/introducing-number-slope) by Volatility. Taken from there:

**Number Slope™** is an original grid deduction puzzle similar to Sudoku. It is solved on an *n*-by-*n* grid, tiled with *n* *n*-ominoes. The rules are:

 - Each number from 1 to *n* must occur once and only once in each row, column, and *n*-omino.
 - Any row or column of adjacent cells *within each* n-*omino* must have numbers which are either increasing or decreasing along the row or column (these are called *slopes*).

That second rule may be a bit confusing, so here is a diagram showing the slopes in an 11-omino and a valid filling:

![slopes](/slope_diagram.png)

Here's another diagram, this time giving an example of the solving process for a 3x3 puzzle. The process is quite similar to solving a Sudoku, but note that in step 3 we can deduce how to fill the vertical tromino, since the numbers have to form a slope.

![solution](/solution_diagram.png)