import pygame
from sys import exit
import numpy as np
import math

width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)

pygame.display.set_caption("Cubic Hermite Curve Demo")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pts = []
count = 0
screen.fill(WHITE)
clock = pygame.time.Clock()

def drawPoint(pt, color=GREEN, thick=3):
    pygame.draw.circle(screen, color, pt, thick)

def drawLine_coordinateFree(pt0, pt1, color=GREEN, thick=3):
    p0 = np.array(pt0)
    p1 = np.array(pt1)
    steps = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])))
    if steps == 0:
        drawPoint(pt0, color, thick)
        return
    for t in np.linspace(0, 1, steps + 1):
        p = (1 - t) * p0 + t * p1
        pt_draw = (int(round(p[0])), int(round(p[1])))
        drawPoint(pt_draw, color, thick)

def get_index_clamped(points, idx):
    if idx < 0:
        return points[0]
    elif idx >= len(points):
        return points[-1]
    return points[idx]

def cubic_hermite(A, B, C, D, t):
    a = -A / 2.0 + (3.0 * B) / 2.0 - (3.0 * C) / 2.0 + D / 2.0
    b = A - (5.0 * B) / 2.0 + 2.0 * C - D / 2.0
    c = -A / 2.0 + C / 2.0
    d = B
    return a * t ** 3 + b * t ** 2 + c * t + d

def draw_cubic_hermite_curve(points, color=RED, thick=2, steps=40):
    n = len(points)
    if n < 2:
        return

    curve_points = []
    for i in range(n - 1):
        A = get_index_clamped(points, i - 1)
        B = get_index_clamped(points, i)
        C = get_index_clamped(points, i + 1)
        D = get_index_clamped(points, i + 2)
        for s in range(steps + 1):
            t = s / steps
            x = cubic_hermite(A[0], B[0], C[0], D[0], t)
            y = cubic_hermite(A[1], B[1], C[1], D[1], t)
            curve_points.append((int(x), int(y)))
    if len(curve_points) > 1:
        pygame.draw.lines(screen, color, False, curve_points, thick)

done = False
pressed = 0
margin = 6
old_pressed = 0
old_button1 = 0

while not done:
    time_passed = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed = -1
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed = 1
        elif event.type == pygame.QUIT:
            done = True
        else:
            pressed = 0

    button1, button2, button3 = pygame.mouse.get_pressed()
    x, y = pygame.mouse.get_pos()
    pt = [x, y]
    pygame.draw.circle(screen, RED, pt, 0)

    if old_pressed == -1 and pressed == 1 and old_button1 == 1 and button1 == 0:
        pts.append(pt)
        count += 1
        pygame.draw.rect(screen, BLUE, (pt[0] - margin, pt[1] - margin, 2 * margin, 2 * margin), 5)

    # 초기화 조건: 우클릭 또는 점이 너무 많아졌을 때
    if button3 or len(pts) > 20:
        screen.fill(WHITE)
        pts = []
        count = 0

    # 화면 지우고 다시 그림
    screen.fill(WHITE)
    for p in pts:
        drawPoint(p, BLUE, 5)
    if len(pts) > 1:
        for i in range(count-1):
            drawLine_coordinateFree(pts[i], pts[i+1], GREEN, 1)
        draw_cubic_hermite_curve(pts, RED, 2, 40)

    pygame.display.update()
    old_button1 = button1
    old_pressed = pressed

pygame.quit()
