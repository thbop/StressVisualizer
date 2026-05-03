import math, sys
import pygame as pg
from pygame import Vector2 as vec2
from tmatrix import *

TITLE = 'Stress Visualizer'
WIDTH = 1200
HEIGHT = 800
FPS = 60

BLACK = ( 0, 0, 0 )
WHITE = ( 255, 255, 255 )
YELLOW = ( 255, 255, 0 )

FONT_SIZE = 32
SELECTION_PANEL_PADDING = 1
SELECTION_PANEL_OFFSET = 5
SELECTION_PANEL_COLOR = WHITE
SELECTION_PANEL_SELECTED_COLOR = YELLOW

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

class Element:
    def __init__( self, pos: vec2 = vec2(0,0) ):
        self.pos: vec2 = pos
    
    def update( self ):
        pass

    def draw( self ):
        pass

class SelectionPanel(Element):
    def __init__( self, options: list[str] = [] ):
        super().__init__()
        self.options = options
        self.shown = False

        self.width = 0
        for option in self.options:
            w = len( option )
            if self.width < w:
                self.width = w

        self.width *= FONT_SIZE

        self.selected = -1
    
    def show( self ):
        self.shown = True
        mx, my = pg.mouse.get_pos()
        self.pos = vec2( mx, my )
    
    def hide( self ):
        self.shown = False
    
    def update( self ):
        if self.shown:
            mx, my = pg.mouse.get_pos()
            for i, _ in enumerate( self.options ):
                rect = [
                    self.pos.x + SELECTION_PANEL_OFFSET,
                    self.pos.y + i * ( FONT_SIZE + SELECTION_PANEL_PADDING ) + SELECTION_PANEL_OFFSET,
                    self.width, FONT_SIZE
                ]
                if pg.Rect( rect ).collidepoint( mx, my ):
                    self.selected = i

    def draw( self ):
        if self.shown:
            for i, option in enumerate( self.options ):
                x = self.pos.x + SELECTION_PANEL_OFFSET
                y = self.pos.y + i * ( FONT_SIZE + SELECTION_PANEL_PADDING ) + SELECTION_PANEL_OFFSET 
                draw_text( option, ( x, y ), color=( YELLOW if self.selected == i else WHITE ) )


running = True

selection_panel = SelectionPanel(
    options=[
        'Add Point',
        'Add XY Anchor',
        'Add X Anchor',
        'Add Y Anchor'
    ]
)

elements = [ selection_panel ]

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                selection_panel.show()
        
        if event.type == pg.MOUSEBUTTONDOWN:
            selection_panel.hide()

    for element in elements:
        element.update()

    screen.fill( BLACK )

    for element in elements:
        element.draw()

    clock.tick( FPS )
    pg.display.flip()


pg.quit()
sys.exit()