import pygame
from sys import exit
import numpy as np
    
width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)

pygame.display.set_caption("Barycentric coordinates")
  
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

# 방식 1: 공식을 이용한 선 그리기
# y = (y1-y0)/(x1-x0) * (x - x0) + y0
def drawLine_formula(pt0, pt1, color=GREEN, thick=3):
    x0, y0 = pt0
    x1, y1 = pt1
    # 수직선인 경우
    if x0 == x1:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            drawPoint((x0, y), color, thick)
    else:
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

    if old_pressed == -1 and pressed == 1 and old_button1 == 1 and button1 == 0 :
        pts.append(pt) 
        count += 1
        pygame.draw.rect(screen, BLUE, (pt[0]-margin, pt[1]-margin, 2*margin, 2*margin), 5)
        # print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed)+" add pts ...")
    else:
        pass
        # print("len:"+repr(len(pts))+" mouse x:"+repr(x)+" y:"+repr(y)+" button:"+repr(button1)+" pressed:"+repr(pressed))

    if len(pts)>1:
        drawPolylines(GREEN, 1)
        # drawLagrangePolylines(BLUE, 10, 3)
    
    if len(pts) == 3:
        
        barycentric_coords, barycentric_coords_point = compute_barycentric_triangle(pt, pts)
        # print(f"Barycentric coordinates: {barycentric_coords}. {barycentric_coords_point}")
        
        screen.fill(WHITE)
        drawLine_coordinateFree(pts[0], pts[1], GREEN, 1)
        drawLine_coordinateFree(pts[1], pts[2], GREEN, 1)
        drawLine_coordinateFree(pts[0], pts[2], GREEN, 1)
        pygame.draw.circle(screen, RED, [x, y], 5)
        myText = myFont.render(f"({round(barycentric_coords[0], 2)}, {round(barycentric_coords[1], 2)}, {round(barycentric_coords[2], 2)})", True, (0, 0, 255))
        screen.blit(myText, (x, y))
                
        drawLine_coordinateFree(pts[0], pts[2], GREEN, 1)
    
    if button3 == True or len(pts) > 3:
        screen.fill(WHITE)
        pts = []
        count = 0

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.update()
    old_button1 = button1
    old_pressed = pressed

pygame.quit()