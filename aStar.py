# A* search Algorithm - Max Malacari 20/02/2017
# Includes random obstacles in the way
# Diagonal movement included
# Can't move diagonally "between" obstacles

import pygame as pg
import sys # to handle quit event
import random as rand
from math import *

# Some options to set!
wWidth = 700 # dimensions of the drawing window
wHeight = 700
cols = 100 # number of cells in each dimension
rows = 100
start_i = 0 # start and end cell coordinates (will be guaranteed not a wall)
start_j = 0
end_i = cols
end_j = rows
wallFraction = 0.05 # fraction of cells that contain an obstacle (0.3 nominal)
showBoundaries = False # show bounding boxes for cells

# Some colours
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
white = (255,255,255)
black = (0,0,0)

w = wWidth / cols
h = wHeight / rows

pg.init()
screen = pg.display.set_mode((wWidth,wHeight))
screen.fill(white)

# Class to hold the properties of a cell
class Cell():
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbours = []
        self.previous = 0
        self.isWall = False

        if rand.random() < wallFraction:
            self.isWall = True
        if i == start_i and j == start_j:
            self.isWall = False
        if i == end_i - 1 and j == end_j - 1:
            self.isWall = False

    def show(self, colour):
        pg.draw.rect(screen, colour, (self.i*w, self.j*h, w, h), 0)

    def showCellBoundary(self):
        pg.draw.rect(screen, black, (self.i*w, self.j*h, w, h), 1)

    def addNeighbours(self, grid):
        if self.isWall == False: # only add neighbours to non-wall cells
            i = self.i
            j = self.j
            # top/bottom/left/right
            if i < cols-1 and grid[i+1][j].isWall == False:
                self.neighbours.append(grid[i+1][j])
            if j < rows-1 and grid[i][j+1].isWall == False:
                self.neighbours.append(grid[i][j+1])
            if i > 0 and grid[i-1][j].isWall == False:
                self.neighbours.append(grid[i-1][j])
            if j > 0 and grid[i][j-1].isWall == False:
                self.neighbours.append(grid[i][j-1])
            # diagonals, also check blocks adjacent to diagonals are not walls
            if i > 0 and j > 0 and grid[i-1][j-1].isWall == False and grid[i][j-1].isWall == False and grid[i-1][j].isWall == False:
                self.neighbours.append(grid[i-1][j-1])
            if i < cols-1 and j > 0 and grid[i+1][j-1].isWall == False and grid[i][j-1].isWall == False and grid[i+1][j].isWall == False:
                self.neighbours.append(grid[i+1][j-1])
            if i > 0 and j < rows-1 and grid[i-1][j+1].isWall == False and grid[i-1][j].isWall == False and grid[i][j+1].isWall == False:
                self.neighbours.append(grid[i-1][j+1])
            if i < cols-1 and j < rows-1 and grid[i+1][j+1].isWall == False and grid[i+1][j].isWall == False and grid[i][j+1].isWall == False:
                self.neighbours.append(grid[i+1][j+1])

def main():

    grid = []
    setup(grid, cols, rows)

    start = grid[start_i][start_j]
    end = grid[end_i-1][end_j-1]

    openSet = []
    closedSet = []
    wallSet = []
    for i in range(0,cols):
        for j in range(0,rows):
            if grid[i][j].isWall:
                wallSet.append(grid[i][j])

    openSet.append(start)
    finished = False

    while finished==False:

        path = []
        # Show wall cells
        for i in range(0,len(wallSet)):
            wallSet[i].show(black)
        # Show cells in the open set
        for i in range(0,len(openSet)):
            openSet[i].show(green)
        # Show cells in the closed set
        for i in range(0,len(closedSet)):
            closedSet[i].show(red)

        # Algorithm
        if len(openSet) > 0:
            lowestCostIndex = 0
            current = openSet[lowestCostIndex]

            for i in range(0,len(openSet)):
                if openSet[i].f < openSet[lowestCostIndex].f:
                    lowestCostIndex = i
                    current = openSet[lowestCostIndex]
            if current == end:
                finished = True
                path = calculatePath(current) # get optimal path
                print "Solution found!"

            else:
                closedSet.append(current)
                openSet.remove(current)

                neighbours = current.neighbours
                for i in range(0,len(neighbours)):
                    neighbour = neighbours[i]
                    neighbour.h = heuristic(neighbour, end)
                    if neighbour in closedSet:
                        continue
                    temp_g = current.g + sqrt((neighbour.i - current.i)**2 + (neighbour.j - current.j)**2) # movement cost to get to neighbour
                    if neighbour in openSet: # is neighbour already in the open set?
                        if temp_g < neighbour.g: # did we get there more efficiently?
                            neighbour.g = temp_g
                            neighbour.f = neighbour.h + neighbour.g
                            neighbour.previous = current
                    else:
                        neighbour.g = temp_g
                        neighbour.f = neighbour.h + neighbour.g
                        neighbour.previous = current
                        openSet.append(neighbour)

                    path = calculatePath(current) # get the current path to this cell

        else:
            finished = True # to quit the loop
            print "No solution!"

        # Show the current path
        ptList = []
        for i in range(0,len(path)):
            #path[i].show(blue)
            ptList.append((path[i].i*w + w/2, path[i].j*h + h/2))
        if len(path) > 1:
            showLine(ptList, blue)

        # Show bounding boxes
        if showBoundaries == True:
            for i in range(0,cols):
                for j in range(0,rows):
                    grid[i][j].showCellBoundary()

        # show end points
        start.show(yellow)
        end.show(yellow)

        # Update the display with new draw objects
        pg.display.update()


    # Stop from instantly closing on finish
    while(True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit();

# Set up the grid of cell objects
def setup(grid, cols, rows):
    for i in range(0,cols):
        grid.append([])
        for j in range(0,rows):
            grid[i].append(Cell(i,j))

    # add neighbours once grid is initialized
    for i in range(0,cols):
        grid.append([])
        for j in range(0,rows):
            grid[i][j].addNeighbours(grid)

def heuristic(cell1, cell2):
    #h = abs(cell1.i - cell2.i) + abs(cell1.j - cell2.j)
    h = sqrt((cell1.i-cell2.i)**2 + (cell1.j-cell2.j)**2)
    return h

def calculatePath(current): # get current optimal path up to current cell
    path = []
    temp = current
    path.append(temp)
    while temp.previous:
        path.append(temp.previous)
        temp = temp.previous
    return path

def showLine(ptList, colour):
    pg.draw.lines(screen, colour, False, ptList, 7)

main()
