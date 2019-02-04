import pygame
import engine
import sys

##constants
FPS = 60
SCRN_SIZE = engine.get_resolution()
SPEED = 50


##pygame setup
pygame.init()
surface = pygame.display.set_mode(SCRN_SIZE, pygame.FULLSCREEN)
clock = pygame.time.Clock()

#makes the mouse cursor invisible while the program is running
pygame.mouse.set_visible(False)


##engine setup
def pointdraw(colour, point):
    pygame.draw.circle(surface,colour,point,8)

def linedraw(colour, point1, point2):
    pygame.draw.line(surface, colour, point1, point2, 6)

engine.point_draw_function = pointdraw
engine.line_draw_function = linedraw


##objects

#the camera object
camera = engine.Camera([0,0,0], [0,0,0])

#all the shapes
cube1 = engine.Cuboid(100,400,100,1000,1000,1000,(255,0,0))
cube2 = engine.Cuboid(-500,-500,-500,1000,1000,1000,(0,0,255))
tetrahedron = engine.Tetrahedron(2000,5000,4500,2100,(31, 111, 209))
line = engine.Line([3203,4290,8074],[164,899,900],16, (0,0,0))


##program loop
running = True
while running:
    ##events/inputs
    for event in pygame.event.get():
        #if the window is closed
        if event.type == pygame.QUIT:
            running = False

        #event handling for movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                camera.spd[2] = -SPEED
            if event.key == pygame.K_a:
                camera.spd[0] = SPEED
            if event.key == pygame.K_s:
                camera.spd[2] = SPEED
            if event.key == pygame.K_d:
                camera.spd[0] = -SPEED
            if event.key == pygame.K_SPACE:
                camera.spd[1] = SPEED
            if event.key == pygame.K_LSHIFT:
                camera.spd[1] = -SPEED

            #reset functionality if r is pressed
            if event.key == pygame.K_r:
                camera.pos = [0,0,0]
                camera.angle = [0,0,0]

            #exit game loop
            if event.key == pygame.K_q:
                running = False

        #stops movement when a movement key is released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                camera.spd[2] = 0
            if event.key == pygame.K_a:
                camera.spd[0] = 0
            if event.key == pygame.K_s:
                camera.spd[2] = 0
            if event.key == pygame.K_d:
                camera.spd[0] = 0
            if event.key == pygame.K_SPACE:
                camera.spd[1] = 0
            if event.key == pygame.K_LSHIFT:
                camera.spd[1] = 0

    #rotate camera according to the direction the mouse moves
    mouse_mov = pygame.mouse.get_rel()
    camera.rotate([mouse_mov[1]/8,mouse_mov[0]/8,0])


    ##logic
    
    #update camera rotation and position - this MUST happen before any transformations
    camera.update()

    #translations
    cube2.rotate([-1,1,0], [0,0,0])
    cube1.rotate([0,1,0], [600,900,600])
    
    #draw onto surface

    #clears all shapes from surface
    surface.fill((255,255,255))

    #draws all the shapes, but just their edges
    cube1.draw(camera, circles=False)
 
    #next frame
    clock.tick(FPS)
    pygame.display.update()

##quit pygame and exit program
pygame.quit()
sys.exit()
