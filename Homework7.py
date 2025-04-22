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

def drawCubicBSpline(points, color=GREEN, thick=3, steps=100):
    """
    제어점들을 통과하는 3차 B-스플라인 곡선을 그립니다.
    
    Args:
        points: 제어점 리스트
        color: 곡선 색상
        thick: 곡선 두께
        steps: 각 세그먼트당 계산할 점의 수
    """
    n = len(points)
    
    # 3차 B-스플라인은 최소 4개의 제어점이 필요
    if n < 4:
        return
    
    # steps가 최소 1이상이 되도록 함
    steps = max(1, steps)
    
    # 각 세그먼트에 대해 B-스플라인 곡선 그리기
    for i in range(n - 3):
        p0 = np.array(points[i])
        p1 = np.array(points[i + 1])
        p2 = np.array(points[i + 2])
        p3 = np.array(points[i + 3])
        
        for j in range(steps + 1):  # +1은 끝점 포함
            u = j / float(steps)
            
            # 3차 B-스플라인의 기저 함수 계산
            b0 = (1 - u)**3 / 6.0
            b1 = (3*u**3 - 6*u**2 + 4) / 6.0
            b2 = (-3*u**3 + 3*u**2 + 3*u + 1) / 6.0
            b3 = u**3 / 6.0
            
            # B-스플라인 상의 점 계산
            p = b0 * p0 + b1 * p1 + b2 * p2 + b3 * p3
            pt = (int(round(p[0])), int(round(p[1])))
            drawPoint(pt, color, thick)

def drawBSplinePolylines(color=GREEN, thick=3):
    if count < 4:
        # 제어점이 4개 미만이면 기존 폴리라인 그리기 방식 사용
        drawPolylines(color, thick)
    else:
        # 제어점 표시
        for i in range(count):
            drawPoint(pts[i], BLUE, thick + 2)
        # B-스플라인 곡선 그리기
        drawCubicBSpline(pts, color, thick)


def compute_barycentric_triangle(point, triangle):
    """
    삼각형에 대한 점의 무게중심좌표를 계산합니다.
    np.linalg.inv를 사용하여 계산합니다.
    
    Args:
        point: 점의 [x, y] 좌표
        triangle: 삼각형을 형성하는 3개의 점 [a, b, c]
        
    Returns:
        무게중심좌표 [u, v, w]
    """
    a, b, c = triangle
    
    # 변환 행렬 생성
    T = np.array([
        [a[0] - c[0], b[0] - c[0]],
        [a[1] - c[1], b[1] - c[1]]
    ])
    
    # 역행렬 계산 (np.linalg.inv 사용)
    try:
        T_inv = np.linalg.inv(T)
    except np.linalg.LinAlgError:
        # 특이 케이스 처리
        return [0, 0, 0]
    
    # 처음 두 무게중심좌표 계산
    point_vector = np.array([point[0] - c[0], point[1] - c[1]])
    lambda1_lambda2 = T_inv.dot(point_vector)
    
    # 세 번째 좌표는 λ₁ + λ₂ + λ₃ = 1 제약조건 사용
    lambda3 = 1 - lambda1_lambda2[0] - lambda1_lambda2[1]
    
    return [lambda1_lambda2[0], lambda1_lambda2[1], lambda3], [lambda1_lambda2[0]*a[0] + lambda1_lambda2[1]*b[0] + lambda3*c[0], lambda1_lambda2[0]*a[1] + lambda1_lambda2[1]*b[1] + lambda3*c[1]]



#Loop until the user clicks the close button.
done = False
pressed = 0
margin = 6
old_pressed = 0
old_button1 = 0


myFont = pygame.font.SysFont(None, 50)

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
    
    if len(pts) >= 3:
        barycentric_coords, barycentric_coords_point = compute_barycentric_triangle(pt, pts[:3])
        # print(f"Barycentric coordinates: {barycentric_coords}. {barycentric_coords_point}")    
        screen.fill(WHITE)
        
        pt0, pt0_ = compute_barycentric_triangle(pts[0], pts[:3])
        pt1, pt1_ = compute_barycentric_triangle(pts[1], pts[:3])
        pt2, pt2_ = compute_barycentric_triangle(pts[2], pts[:3])
    
        pygame.draw.circle(screen, RED, [x, y], 5)
        myText = myFont.render(f"({round(barycentric_coords[0], 2)}, {round(barycentric_coords[1], 2)}, {round(barycentric_coords[2], 2)})", True, (0, 0, 255))
        screen.blit(myText, (x, y))

    if old_pressed == -1 and pressed == 1 and old_button1 == 1 and button1 == 0 :
        pts.append(pt) 
        count += 1
        pygame.draw.rect(screen, BLUE, (pt[0]-margin, pt[1]-margin, 2*margin, 2*margin), 5)
        print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed)+" add pts ...")
    else:
        print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed))
    
    drawPolylines('GREEN', thick=1)
    
    if len(pts) >= 4:  # 제어점이 4개 이상일 때 B-스플라인 사용
        drawBSplinePolylines(GREEN, 1)
        

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.update()
    old_button1 = button1
    old_pressed = pressed

pygame.quit()