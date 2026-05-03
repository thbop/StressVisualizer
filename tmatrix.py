'''
Copyright © 2026 Thbop

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# This code was written for school, so it might be sketchy

import math

def sub_lists( a: list, b: list ):
    if len( a ) != len( b ): return None
    return [ a[i] - b[i] for i, _ in enumerate( a ) ]

def mul_value_list( value, array: list ):
    return [ value * element for element in array ]


class tlist(list):
    def __getitem__( self, index ):
        if 0 <= index and index < self.__len__():
            return super().__getitem__( index )
        
        return ( 0
                if isinstance( super().__getitem__( 0 ), int ) or
                isinstance( super().__getitem__( 0 ), float )
                else tlist([0])
        )
    
    
    # def __setitem__( self, index, value ):
    #     if 0 <= index and index < self.__len__():
    #         return super().__setitem__( index, value )


class InvalidMatrix(Exception): pass


class Matrix:
    def __init__( self, data: list ):
        self._data = tlist( data )
        for i, row in enumerate( self._data ): self._data[i] = row.copy()
        self.size_y = len( data )
        self.size_x = len( data[0] )

    # Factories
    @staticmethod
    def zero( size_x: int, size_y: int ):
        m = Matrix( [ [ 0 for _ in range( size_x ) ] for _ in range( size_y ) ] )
        return m
    
    @staticmethod
    def identity( size: int ):
        m = Matrix( [ [ 1 if i == j else 0 for i in range( size ) ] for j in range( size ) ] )
        return m
    
    # Methods
    def normalized_rows( self ):
        m = self.copy()
        for row in m._data:
            max_value = 0
            for v in row:
                max_value = abs( v ) if abs( v ) > max_value else max_value
            for i, _ in enumerate( row ):
                row[i] /= max_value
        
        return m

    def fnorm( self ):
        f = 0
        for row in self._data:
            for v in row:
                f += v*v
        
        return math.sqrt( f )
    
    def row_sum_norm( self ):
        max_row = 0
        for row in self._data:
            row_abs_sum = 0
            for v in row: row_abs_sum += abs( v )

            if row_abs_sum > max_row: max_row = row_abs_sum
        
        return max_row
        
    def copy( self ):
        return Matrix( self._data )

    def swap_rows( self, rowi0: int, rowi1: int ):
        if rowi0 >= self.size_y or rowi1 >= self.size_y:
            return
        if rowi0 == rowi1:
            return

        row0 = self.get_row( rowi0 )
        row1 = self.get_row( rowi1 )
        self.set_row( rowi1, row0 )
        self.set_row( rowi0, row1 )


    # Setters
    def set_row( self, row: int, values: list ):
        if len( values ) == self.size_x and 0 <= row and row < self.size_y:
            self._data[row] = values[:]
    
    # Getters
    def get_row( self, row: int ):
        if 0 <= row and row < self.size_y:
            return self._data[row]
        
    def transpose( self ):
        m = Matrix.zero( self.size_y, self.size_x )

        for j in range( m.size_y ):
            for i in range( m.size_x ):
                m[ i, j ] = self[ j, i ]
        
        return m
    
    # Overloads
    def __getitem__( self, key: tuple ):
        i, j = key
        if i < 0 or i > self.size_x - 1 or j < 0 or j > self.size_y - 1:
            return 0
        return self._data[j][i]

    
    def __setitem__( self, key: tuple, value ):
        i, j = key
        if i < 0 or i > self.size_x - 1 or j < 0 or j > self.size_y - 1:
            return
        self._data[j][i] = value

    def __mul__( self, other ):
        if isinstance( other, float ) or isinstance( other, int ):
            m = self.copy()
            for row in m._data:
                for i, _ in enumerate( row ):
                    row[i] *= other
            
            return m

        if isinstance( other, Matrix ):
            if self.size_x != other.size_y:
                raise InvalidMatrix( 'Dimension error!' )
            
            m = Matrix.zero( other.size_x, self.size_y )

            for j in range( self.size_y ):
                for i in range( other.size_x ):
                    v = 0
                    for k in range( self.size_x ):
                        v += self[ k, j ] * other[ i, k ]
                    m[i, j] = v
            
            return m

    
    def __rmul__( self, other ):

        if isinstance( other, list ):
            return Matrix( other ) * self
        return self.__mul__( other )


    def __truediv__( self, other ):
        if isinstance( other, float ) or isinstance( other, int ):
            return self.__mul__( 1.0 / other )

    
    def __str__( self ):
        out = ''
        for i, row in enumerate( self._data ):
            if i > 0: out += '\n'
            out += str( row ).replace( ',', '' )
        return out

class LUDecomp:
    def __init__( self, m: Matrix|list ):
        if isinstance( m, list ):
            m = Matrix( m )
        else:
            m = m.copy()

        if m.size_x < 2 or m.size_x != m.size_y:
            raise InvalidMatrix( 'Invalid matrix!' )

        n = m.size_x

        # Employ partial pivoting
        self.swaps = [ (i,i) for i in range( n ) ]
        for i in range( n ):
            max_value = abs( m[i, i] )
            pivot_row = i
            for k in range( i + 1, n ):
                if ( abs( m[i, k] ) > max_value ):
                    max_value = abs( m[i, k] ) 
                    pivot_row = k
            
            if max_value < 1e-12:
                raise ValueError( 'Singular matrix error!' )
            
            if pivot_row != i:
                m.swap_rows( i, pivot_row )
                self.swaps[i] = (i, pivot_row)


        self.L: Matrix = Matrix.identity( m.size_x )
        self.U: Matrix = m.copy()

        for pi in range( n - 1 ): # pivot index
            inv_pivot = 1.0 / self.U[ pi, pi ]
            for ri in range( n - 1 - pi ): # rows below to set to zero
                self.L[ pi, pi + ri + 1 ] = self.U[ pi, pi + ri + 1 ] * inv_pivot
                self.U[ pi, pi + ri + 1 ] = 0
                for ci in range( n - 1 - pi ): # a primes for other cols
                    self.U[ pi + ci + 1, pi + ri + 1 ] -= self.L[ pi, pi + ri + 1 ] * self.U[ pi + ci + 1, pi ]
        
        

    @staticmethod
    def _substitute_triangle( T: Matrix, S: Matrix, upper=True ) -> Matrix:
        X = S.copy()
        for j, row in enumerate( reversed( T._data ) if upper else T._data ):
            c = T.size_y - j - 1 if upper else j
            
            look_range = range( c + 1, T.size_y ) if upper else range( c )
            
            for i in look_range: X[0, c] -= X[0, i] * row[i]
            X[0, c] /= row[c]
        
        return X
    
    def solve( self, B: Matrix|list ) -> Matrix:
        if isinstance( B, list ):
            B = Matrix( B )
        else:
            B = B.copy()
        
        if B.size_y != self.L.size_x: return None

        for i, j in self.swaps:
            B.swap_rows( i, j )

        D = LUDecomp._substitute_triangle( self.L, B, upper=False )
        X = LUDecomp._substitute_triangle( self.U, D )

        return X
    

def lu_inverse_solver( m: Matrix ):
    if isinstance( m, list ):
        m = Matrix( m )

    lu = LUDecomp( m ) # handles invalid matrices
    im = Matrix.zero( m.size_x, m.size_y )
    for i in range( m.size_x ):
        B = [ [ 1 if i == j else 0 ] for j in range( m.size_y ) ]
        X = lu.solve( B )
        for j in range( m.size_y ):
            im[ i, j ] = X[ 0, j ]
    
    return im

if __name__ == '__main__':
    # lu = LUDecomp([
    #     [ -2,  7,  2 ],
    #     [ -4, 20,  8 ],
    #     [-10, -1, -6 ],
    # ])

    # B = Matrix([
    #     [ 1 ],
    #     [ 5 ],
    #     [ 6 ],
    # ])

    # X = lu.solve( B )
    # print( X )

    m = Matrix([
        [0,3,5,7],
        [2,7,1,9],
        [1,4,0,1],
        [9,2,4,2]
    ])
    im = lu_inverse_solver( m )
    print( im * m )
