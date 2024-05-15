import pygame as pg
import sys, math
from enum import Enum

vec2 = pg.math.Vector2

WIDTH = 600
HEIGHT = 600
CENTER = vec2(WIDTH // 2, HEIGHT // 2)

CELL_SIZE = 30
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 210)
RED = (255, 0, 0)
BLUE = (0,0,255)

FPS = 60
PI = math.pi
