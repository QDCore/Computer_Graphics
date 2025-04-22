"""
Modified on Feb 20 2020
@author: lbg@dongseo.ac.kr
"""

import pygame
from sys import exit
import numpy as np
    
width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)

pygame.display.set_caption("ImagePolylineMouseButton")
  
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

pts = [] 
knots = []
count = 0
#screen.blit(background, (0,0))
screen.fill(WHITE)

# https://kite.com/python/docs/pygame.Surface.blit
clock= pygame.time.Clock()


def drawPoint(pt, color='GREEN', thick=3):
    # pygame.draw.line(screen, color, pt, pt)
    pygame.draw.circle(screen, color, pt, thick)

#HW2 implement drawLine with drawPoint
# y = (y1-y0)/(x1-x0) * (x - x0) + y0
def drawLine_formula(pt0, pt1, color=GREEN, thick=3):
    x0, y0 = pt0
    x1, y1 = pt1
    # 수직선인 경우
    # if x0 == x1:
    #     for y in range(min(y0, y1), max(y0, y1) + 1):
    #         drawPoint((x0, y), color, thick)
    # else:
    slope = (y1 - y0) / (x1 - x0)
    for x in range(min(x0, x1), max(x0, x1) + 1):
        y = int(slope * (x - x0) + y0)
        drawPoint((x, y), color, thick)

# 방식 2: 좌표 자유 시스템 (선형 보간: a0*p0 + a1*p1)
def drawLine_coordinateFree(pt0, pt1, color=GREEN, thick=3):
    p0 = np.array(pt0)
    p1 = np.array(pt1)
    # 보간 단계를 결정 (x나 y 좌표의 최대 차이를 사용)
    steps = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])))
    if steps == 0:
        drawPoint(pt0, color, thick)
        return
    for t in np.linspace(0, 1, steps + 1):
        # 선형 보간: (1-t)*p0 + t*p1
        p = (1 - t) * p0 + t * p1
        pt_draw = (int(round(p[0])), int(round(p[1])))
        drawPoint(pt_draw, color, thick)


def drawLine(pt0, pt1, color='GREEN', thick=3):
    drawPoint((100,100), color,  thick)
    drawPoint(pt0, color, thick)
    drawPoint(pt1, color, thick)

def drawPolylines(color='GREEN', thick=3):
    if(count < 2): return
    for i in range(count-1):
        # drawLine(pts[i], pts[i+1], color)
        # drawLine_formula(pts[i], pts[i + 1], color, thick)
        drawLine_coordinateFree(pts[i], pts[i + 1], color, thick)
        # pygame.draw.line(screen, color, pts[i], pts[i+1], thick)
def lagrange_basis(j, x, X):
    """
    라그랑주 기저 다항식 L_j(x)를 계산합니다.
    
    Args:
        j: 기저 다항식의 인덱스
        x: 계산할 지점
        X: 모든 점의 x 좌표 리스트
    
    Returns:
        x에서의 j번째 라그랑주 기저 다항식 값
    """
    n = len(X)
    result = 1.0
    for i in range(n):
        if i != j:
            # 분모가 0이 될 수 있는 경우 처리
            if X[j] == X[i]:
                return 0.0
            result *= (x - X[i]) / (X[j] - X[i])
    return result

def lagrange_interpolate(x, X, Y):
    """
    라그랑주 보간법을 사용하여 x에서의 함수값을 계산합니다.
    
    Args:
        x: 계산할 지점
        X: 모든 점의 x 좌표 리스트
        Y: 모든 점의 y 좌표 리스트
    
    Returns:
        x에서의 보간된 함수값
    """
    n = len(X)
    result = 0.0
    for j in range(n):
        result += Y[j] * lagrange_basis(j, x, X)
    return result

def drawLagrangePolylines(color=BLUE, steps=100, thick=3):
    """
    라그랑주 보간법을 사용하여 부드러운 곡선을 그립니다.
    
    Args:
        color: 그릴 곡선의 색상
        steps: 곡선을 얼마나 부드럽게 그릴지 결정하는 단계 수
        thick: 점의 두께
    """
    n = len(pts)
    if n < 3:
        return
    
    # x, y 좌표 추출
    X = [pt[0] for pt in pts]
    Y = [pt[1] for pt in pts]
    
    # 보간할 x 범위 계산
    x_min = min(X)
    x_max = max(X)
    
    # 곡선 그리기
    prev_point = None
    for i in range(steps + 1):
        x = x_min + (x_max - x_min) * i / steps
        try:
            y = lagrange_interpolate(x, X, Y)
            
            # 화면 크기를 벗어나는 값은 건너뜀
            if y < -1000 or y > height + 1000:
                prev_point = None
                continue
            
            # y 좌표가 화면 범위 내에 있도록 조정
            y = max(0, min(height - 1, y))
            
            point = (int(x), int(y))
            drawPoint(point, color, thick)
            
            # 연속된 점을 선으로 연결하여 부드러운 곡선 생성
            if prev_point is not None:
                drawLine_coordinateFree(prev_point, point, color, thick-1)
            
            prev_point = point
        except Exception as e:
            print(f"라그랑주 다항식 계산 오류: {e}")
            prev_point = None
            continue

#Loop until the user clicks the close button.
done = False
pressed = 0
margin = 6
old_pressed = 0
old_button1 = 0

while not done:   
    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
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

    if old_pressed == -1 and pressed == 1 and old_button1 == 1 and button1 == 0 :
        pts.append(pt) 
        count += 1
        pygame.draw.rect(screen, BLUE, (pt[0]-margin, pt[1]-margin, 2*margin, 2*margin), 5)
        print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed)+" add pts ...")
    else:
        print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed))
    
    
    if len(pts)>1:
        screen.fill(WHITE)
        for pt in pts:
            pygame.draw.rect(screen, BLUE, (pt[0]-margin, pt[1]-margin, 2*margin, 2*margin), 5)
        drawPolylines(GREEN, 1)
        drawLagrangePolylines(BLUE, 100, 3)  # 라그랑주 보간법 곡선 추가


    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.update()
    old_button1 = button1
    old_pressed = pressed

pygame.quit()