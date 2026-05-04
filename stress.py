import math, sys
import pygame as pg
from pygame import Vector2 as vec2
from tmatrix import *

TITLE = 'Stress Visualizer'
WIDTH = 1200
HEIGHT = 800
FPS = 60

BLACK = ( 0, 0, 0 )
REALLY_DARK_GRAY = ( 10, 10, 10 )
DARK_GRAY = ( 30, 30, 30 )
WHITE = ( 255, 255, 255 )
YELLOW = ( 255, 255, 0 )
LIGHT_BLUE = ( 60, 220, 255 )
MAGENTA = ( 255, 0, 255 )
GRAY = ( 100, 100, 100 )
RED = ( 255, 0, 0 )

FONT_SIZE = 32

CURSOR_SIZE = 32
CURSOR_WIDTH = 2

GRID_COLOR = DARK_GRAY
GRID_CELL_SIZE = 32

SELECTION_PANEL_PADDING = 1
SELECTION_PANEL_OFFSET = 5
SELECTION_PANEL_COLOR = WHITE
SELECTION_PANEL_SELECTED_COLOR = YELLOW

POINT_COLOR = WHITE
POINT_HOVER_COLOR = LIGHT_BLUE
POINT_SELECTED_COLOR = MAGENTA
POINT_RADIUS = 6
POINT_SQR_RADIUS = POINT_RADIUS*POINT_RADIUS

CONNECTION_COLOR = GRAY
CONNECTION_STRESSED_COLOR = RED

pg.init()

pg.display.set_caption( TITLE )
screen = pg.display.set_mode( ( WIDTH, HEIGHT ) )
pg.mouse.set_visible( False )


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

class Grid(Element):
    def __init__( self ):
        super().__init__()

        self.rows = math.ceil( HEIGHT / GRID_CELL_SIZE )
        self.cols = math.ceil( WIDTH / GRID_CELL_SIZE )

    @staticmethod
    def snap_to_grid( pos: vec2 ):
        pos.x = round( pos.x / GRID_CELL_SIZE ) * GRID_CELL_SIZE
        pos.y = round( pos.y / GRID_CELL_SIZE ) * GRID_CELL_SIZE
    
    def update( self ):
        pass

    def draw( self ):
        for i in range( self.cols ):
            pg.draw.line( screen, GRID_COLOR, ( i*GRID_CELL_SIZE, 0 ), ( i*GRID_CELL_SIZE, HEIGHT ), 1 )
        for j in range( self.rows ):
            pg.draw.line( screen, GRID_COLOR, ( 0, j*GRID_CELL_SIZE ), ( WIDTH, j*GRID_CELL_SIZE ), 1 )

class Cursor(Element):
    def __init__( self ):
        self.surf = pg.Surface( ( CURSOR_SIZE, CURSOR_SIZE ) )
        offset = ( CURSOR_SIZE - CURSOR_WIDTH ) / 2
        pg.draw.line( self.surf, WHITE, ( 0, offset ), ( CURSOR_SIZE, offset ), CURSOR_WIDTH )
        pg.draw.line( self.surf, WHITE, ( offset, 0 ), ( offset, CURSOR_SIZE ), CURSOR_WIDTH )

        self._pos = vec2( 0, 0 )
    
    @property
    def pos( self ):
        return self._pos.copy()
    
    def update( self ):
        mx, my = pg.mouse.get_pos()
        self._pos.x = mx
        self._pos.y = my

        if pg.key.get_pressed()[pg.K_LSHIFT]:
            Grid.snap_to_grid( self._pos )

    def draw( self ):
        screen.blit( self.surf, self._pos - vec2( CURSOR_SIZE / 2, CURSOR_SIZE / 2 ), special_flags=pg.BLEND_ADD )


cursor = Cursor()


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

        self.selected = 0
    
    def show( self ):
        self.shown = True
        self.pos = cursor.pos
    
    def hide( self ):
        self.shown = False
    
    def update( self ):
        if self.shown:

            for i, _ in enumerate( self.options ):
                rect = [
                    self.pos.x + SELECTION_PANEL_OFFSET,
                    self.pos.y + i * ( FONT_SIZE + SELECTION_PANEL_PADDING ) + SELECTION_PANEL_OFFSET,
                    self.width, FONT_SIZE
                ]
                if pg.Rect( rect ).collidepoint( cursor.pos.x, cursor.pos.y ):
                    self.selected = i

    def draw( self ):
        if self.shown:
            for i, option in enumerate( self.options ):
                x = self.pos.x + SELECTION_PANEL_OFFSET
                y = self.pos.y + i * ( FONT_SIZE + SELECTION_PANEL_PADDING ) + SELECTION_PANEL_OFFSET 
                draw_text( option, ( x, y ), color=( YELLOW if self.selected == i else WHITE ) )

class Point:
    def __init__( self, pos: vec2 ):
        self.pos = pos

        self.is_selected = False

    @property
    def is_hovered( self ) -> bool:
        return cursor.pos.distance_squared_to( self.pos ) <= POINT_SQR_RADIUS
    
    
    def update( self ):
        pass

    def draw( self ):
        pg.draw.aacircle( screen, POINT_COLOR, self.pos, POINT_RADIUS )

        if self.is_hovered:
            pg.draw.aacircle( screen, POINT_HOVER_COLOR, self.pos, POINT_RADIUS+4, width=2 )
        if self.is_selected:
            pg.draw.aacircle( screen, POINT_SELECTED_COLOR, self.pos, POINT_RADIUS+4, width=2 )

class Points(Element):
    def __init__( self ):
        super().__init__()

        self.points: list[Point] = []
        self.connections: list[tuple[Point, Point]] = []

        self.selected = None

    def is_connected_to_selected( self, point_id: int ):
        for conn in self.connections:
            if self.selected in conn and point_id in conn:
                return True
        return False

    def connect_to_selected( self, point ):
        if self.selected:
            if self.is_connected_to_selected( point ):
                return
            self.connections.append( ( self.selected, point ) )

    def add( self, point: Point ):
        self.connect_to_selected( point )
        self.points.append( point )
    
    def clear( self ):
        self.points.clear()
        self.connections.clear()
        self.selected = None
    
    
    def remove_selected( self ):
        if self.selected:
            removed = []
            for conn in self.connections:
                if self.selected in conn:
                    removed.append( conn )
            for conn in removed:
                self.connections.remove( conn )

            self.points.remove( self.selected )
            self.selected = None
    
    def clear_selected( self ):
        if self.selected:
            self.selected.is_selected = False
            self.selected = None
    
    def update( self ):
        for p in self.points:
            if p.is_hovered:
                if pg.mouse.get_pressed()[0]:
                    self.clear_selected()
                    p.is_selected = True
                    self.selected = p
                elif pg.mouse.get_pressed()[1]:
                    if p != self.selected:
                        self.connect_to_selected( p )
            p.update()

    def draw( self ):
        for p0, p1 in self.connections:
            pg.draw.aaline( screen, CONNECTION_COLOR, p0.pos, p1.pos )
        for p in self.points:
            p.draw()

    

running = True

selection_panel = SelectionPanel(
    options=[
        'Add Point',
        'Remove Point',
        'Add XY Anchor',
        'Add X Anchor',
        'Add Y Anchor',
        'Clear',
    ]
)

points = Points()
grid = Grid()

elements = [
    grid,
    cursor,
    points,
    selection_panel,
]


def process_selection( selection ):
    match selection:
        case 0: # Add Point
            points.add( Point( cursor.pos ) )
        case 1: # Remvoe Point
            points.remove_selected()
        
        case 5: # Clear
            points.clear()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                selection_panel.hide()
                points.clear_selected()
        
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                selection_panel.show()

            elif event.button == 1 and selection_panel.shown:
                process_selection( selection_panel.selected )
                selection_panel.hide()

    for element in elements:
        element.update()

    screen.fill( REALLY_DARK_GRAY )

    for element in elements:
        element.draw()

    clock.tick( FPS )
    pg.display.flip()


pg.quit()
sys.exit()