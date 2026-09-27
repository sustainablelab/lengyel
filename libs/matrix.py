#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Matrix and vector math.

Emulating numeric types:
    https://docs.python.org/3.6/reference/datamodel.html?highlight=data%20model#emulating-numeric-types
"""

class Vector3D:
    def __init__(self, x:float,y:float,z:float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self) -> str:
        return f"({self.x},{self.y},{self.z})"

    def __mul__(self, s:float) -> 'Vector3D':
        """Multiplication by a scalar.

        >>> v = Vector3D(1,2,3)
        >>> v*2
        (2,4,6)
        """
        x = s * self.x
        y = s * self.y
        z = s * self.z
        return Vector3D(x,y,z)

    def __rmul__(self, s:float) -> 'Vector3D':
        """Handle s*v (Vector3D is right operand).

        >>> v = Vector3D(1,2,3)
        >>> 2*v
        (2,4,6)
        """
        return self*s

    def __truediv__(self, s:float) -> 'Vector3D':
        """Division by a scalar.

        >>> v = Vector3D(10,11,12)
        >>> v/10
        (1.0,1.1,1.2)
        """
        x = self.x/s
        y = self.y/s
        z = self.z/s
        return Vector3D(x,y,z)

    def __neg__(self) -> 'Vector3D':
        """Negate each component.

        >>> v = Vector3D(1,2,3)
        >>> -v
        (-1,-2,-3)
        >>> --v
        (1,2,3)
        >>> v = Vector3D(-1,-2,-3)
        >>> -v
        (1,2,3)
        """
        x = -1*self.x
        y = -1*self.y
        z = -1*self.z
        return Vector3D(x,y,z)

    @property
    def Q(self) -> float:
        """Quadrance.

        >>> v = Vector3D(1,2,3)
        >>> v.Q # 1 + 4 + 9 = 14
        14
        """
        return self.x**2 + self.y**2 + self.z**2

    # def __abs__(self) -> float:

if __name__ == '__main__':
    from pathlib import Path
    print(f"Run doctests in {Path(__file__).name}")
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
