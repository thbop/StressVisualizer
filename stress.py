import math, sys
import pygame as pg
from pygame import Vector2 as vec2
from tmatrix import *

TITLE = 'Stress Visualizer'
WIDTH = 1200
HEIGHT = 800
FPS = 60

FONT_SIZE = 32

BLACK = ( 0, 0, 0 )
WHITE = ( 255, 255, 255 )

pg.init()

pg.display.set_caption( TITLE )
screen = pg.display.set_mode( ( WIDTH, HEIGHT ) )
font = pg.font.Font( size=FONT_SIZE )
clock = pg.time.Clock()


def draw_text( text: str, pos: vec2, color=WHITE ):
    if isinstance( pos, tuple ):
        pos = vec2( pos[0], pos[1] )
    screen.blit( font.render( text, antialias=True, color=color ), [ pos.x, pos.y, 0, 0 ] )

def cos_theta( a: vec2, b: vec2 ):
    return a.dot( b )

def sin_theta( a: vec2, b: vec2 ):
    a_len = a.length()
    b_len = b.length()
    u = ( a_len * b_len )
    v = a.dot( b )
    return math.sqrt( u*u - v*v ) / u

print( sin_theta( vec2( 1, 0 ), vec2( 0, 1 ) ) )

running = True

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill( BLACK )


    clock.tick( FPS )
    pg.display.flip()


pg.quit()
sys.exit()