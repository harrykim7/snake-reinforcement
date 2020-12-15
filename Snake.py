
'''
SNAKE GAME
'''
import numpy as np
import random


class BodyNode():
    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def setParent(self, parent):
        self.parent = parent

    def getPosition(self):
        return (self.x, self.y)
    
    def getIndex(self):
        return (self.y, self.x)


class Snake():
    def __init__(self, x, y):
        self.head = BodyNode(None, x, y)
        self.tail = self.head

    def moveBodyForwards(self):
        currentNode = self.tail
        while currentNode.parent != None:
            parentPosition = currentNode.parent.getPosition()
            currentNode.setX(parentPosition[0])
            currentNode.setY(parentPosition[1])
            currentNode = currentNode.parent

    def move(self, direction):
        (oldTailX, oldTailY) = self.tail.getPosition()
        self.moveBodyForwards()
        headPosition = self.head.getPosition()
        if direction == 0:
            self.head.setY(headPosition[1] - 1)
        elif direction == 1:
            self.head.setX(headPosition[0] + 1)
        elif direction == 2:
            self.head.setY(headPosition[1] + 1)
        elif direction == 3:
            self.head.setX(headPosition[0] - 1)
        return (oldTailX, oldTailY, *self.head.getPosition())

    def newHead(self, newX, newY):
        newHead = BodyNode(None, newX, newY)
        self.head.setParent(newHead)
        self.head = newHead
        
    def getHead(self):
        return self.head
    
    def getTail(self):
        return self.tail


class SnakeGame():
    def __init__(self, width, height):
        # arbitrary numbers to signify head, body, and food)
        # 0 for empty space
        self.headVal = 2
        self.bodyVal = 1
        self.foodVal = 7
        self.width = width
        self.height = height
        self.board = np.zeros([height, width], dtype=int)

        self.length = 1

        startX = width//2
        startY = height//2

        self.board[startX, startY] = self.headVal
        self.snake = Snake(startX, startY)
        self.spawnFood()
        self.calcState()
#        print(self.board)

    def spawnFood(self):
        # spawn food at location not occupied by snake
        emptyCells = []
        for index, value in np.ndenumerate(self.board):
            if value != self.bodyVal and value != self.headVal:
                emptyCells.append(index)
        self.foodIndex = random.choice(emptyCells)
        self.board[self.foodIndex] = self.foodVal

    def checkValid(self, direction):
        # check if move is blocked by wall
        newX, newY = self.potentialPosition(direction)
        if newX == -1 or newX == self.width:
            return False
        if newY == -1 or newY == self.height:
            return False
        # check if move is blocked by snake body
        if self.board[newY, newX] == self.bodyVal:
            return False
        return True

    def potentialPosition(self, direction):
        (newX, newY) = self.snake.getHead().getPosition()
        if direction == 0:
            newY -= 1
        elif direction == 1:
            newX += 1
        elif direction == 2:
            newY += 1
        elif direction == 3:
            newX -= 1
        return (newX, newY)

    def calcState(self):
        # state is as follows.
        # Is direction blocked by wall or snake?
        # Is food in this direction?
        # (top blocked, right blocked, down blocked, left blocked,
        # top food, right food, down food, left food)
        self.state = np.zeros(8, dtype=int)
        for i in range(4):
            self.state[i] = not self.checkValid(i)
        self.state[4:] = self.calcFoodDirection()

    def calcStateNum(self):
        # calculate an integer number for state
        # there will be 2^8 potential states but not all states are reachable
        stateNum = 0
        for i in range(8):
            stateNum += 2**i*self.state[i]
        return stateNum

    def calcFoodDirection(self):
        # food can be 1 or 2 directions eg. right and up
        # 0 is up, 1 is right, 2 is down, 3 is left
        foodDirections = np.zeros(4, dtype=int)
        dist = np.array(self.foodIndex) - np.array(self.snake.getHead().getIndex())
        if dist[0] < 0:
            # down
            foodDirections[0] = 1
        elif dist[0] > 0:
            # up
            foodDirections[2] = 1
        if dist[1] > 0:
            # right
            foodDirections[1] = 1
        elif dist[1] < 0:
            # left
            foodDirections[3] = 1
        return foodDirections

    def makeMove(self, direction):
        gameOver = False
        if self.checkValid(direction):
            # set reward if moving in the right direction
            if self.calcFoodDirection()[direction] == 1:
                reward = 1
            else:
                reward = 0
            (headX, headY) = self.snake.getHead().getPosition()
            # set old head to body val
            self.board[headY, headX] = self.bodyVal

            # check if we got the fruit
            potX, potY = self.potentialPosition(direction)
            if self.board[potY, potX] == self.foodVal:
                # extend the snake
                self.snake.newHead(potX, potY)
                self.board[potY, potX] = self.headVal
                self.spawnFood()
                self.length += 1
                # if you want to give a higher reward for getting the fruit, uncomment below
                reward = 2
            else:
                # move the snake
                (oldTailX, oldTailY, newHeadX, newHeadY) = self.snake.move(direction)
                self.board[oldTailY, oldTailX] = 0
                self.board[newHeadY, newHeadX] = self.headVal
        else:
            reward = -2
            gameOver = True
        self.calcState()
        return (self.calcStateNum(), reward, gameOver, self.length)
