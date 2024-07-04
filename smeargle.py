from typing import Tuple, List, Callable, BinaryIO, Self
import zlib
import struct
import functools
from enum import Enum

Pixel = Tuple[int, int, int]
"""
The function that will generate the image in question,
it takes the pixel coord (and/or other args) and returns the appropriate Pixel for that coord
"""
Generator = Callable[..., Pixel]

"""RGBA Colours"""
BLACK: Pixel = (0, 0, 0, 255)
WHITE: Pixel = (255, 255, 255, 255)
RED: Pixel = (255, 0, 0, 255)
GREEN: Pixel = (0, 255, 0, 255)
BLUE: Pixel = (0, 0, 255, 255)
PURPLE: Pixel = (255, 0, 255, 255)
BLANK: Pixel = (0, 0, 0, 0)

class ColorType(Enum):
    RGB = 2 
    RGBA = 6

class Vec2:
    def __init__(self: Self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Image:
    pass

    def __init__(self: Self, width: int, height: int, data: List[List[Pixel]] | None = None) -> None:

        self.width = width
        self.height = height
        self._data: List[List[Pixel]] = data if data is not None else [[BLANK for _ in range(width)] for _ in range(height)]

    def __iter__(self: Self):
        return iter(self._data)

    def __next__(self: Self):
        return next(self._data)

    def __len__(self: Self) -> int:
        return len(self._data)

    def __getitem__(self: Self, key: int) -> List[Pixel]:
        return self._data[key]

    def from_generator(width: int, height: int, generator: Generator) -> Self:

        return [[generator(i, j) for j in range(width)] for i in range(height)]

    def draw(self: Self, y: int, x: int, color: Pixel) -> None:
        self[y][x] = color

    def draw_rect(self: Self, pos: Vec2, length: int, height: int, color: Pixel) -> None:

        for i in range(len(self)):
            for j in range(len(self[i])):

                if j >= pos.x and j <= pos.x + length and i >= pos.y and i <= pos.y + height: 
                    self.draw(i, j, color)

    def draw_circle(self: Self, pos: Vec2, radius: int, color: Pixel) -> None:

        for i in range(len(self)):
            for j in range(len(self[i])):

                if (i-pos.x)*(i-pos.x) + (j-pos.y)*(j-pos.y) <= radius*radius: 
                    self.draw(i, j, color)

    def draw_line(self: Self, p1: Vec2, p2: Vec2, thickness: int, color: Pixel) -> None:

        """
        draw according to y = mx + (c+t)
        """

        m = (p1.y - p2.y)/(p1.x - p2.x)
        c = p1.y - m*p1.x

        for i in range(len(self)):
            for j in range(len(self[i])):

                if i >= m*j + c  - thickness//2 and i <= m*j + c  + thickness//2: 
                    self.draw(i, j, color)

    def draw_triangle(self: Self, p1: Vec2, p2: Vec2, p3: Vec2, color: Pixel) -> None: 
        """
        Based on: https://jtsorlinis.github.io/rendering-tutorial/
        Shoelace Area of a triangle: |(1/2)*( (x_b - x_a)*(y_c - y_a) - (y_b - y_a)*(x_c - x_a)) | 
        A = |SA|
        EdgeFunction = 2SA
        by convention triangles will be defined clockwise, i.e.
                  p2
                  /\
                 /  \
                /    \
               /      \
              p1------p3

        Determining whether a point is in the triangle is thus
        finding out whether all the edgefunctions are posistive for an arbitrary point p 
        """       
        edgeFunction: Callable[[Vec2, Vec2, Vec2], int] = lambda p1, p2, p3: (p2.x - p1.x)*(p3.y - p1.y) - (p2.y - p1.y)*(p3.x - p1.x)

        for i in range(len(self)):
            for j in range(len(self[i])):
                p = Vec2(j, i)
                abp = edgeFunction(p1, p2, p)
                bcp = edgeFunction(p2, p3, p)
                cap = edgeFunction(p3, p1, p)

                if abp >= 0 and bcp >= 0 and cap >= 0: 
                    self.draw(i, j, color)
        

class PNG:

    def __init__(self: Self, img: Image) -> None:

        assert len(img) > 0, "Expected a non-zero sized image"
        d = b'\x89PNG\r\n\x1A\n'  # Header
        d += self._gen_chunk(b'IHDR', self._ihdr(len(img[0]), len(img), 8, ColorType.RGBA))
        d += self._gen_chunk(b'IDAT', self._idat(img))
        d += self._gen_chunk(b'IEND', b'')

        self._data = d

    def dump_png(self: Self, out: BinaryIO) -> None:
        out.write(self._data)

    def save_png(self: Self, filename: str) -> None:

        with open(filename, 'wb') as f:
            self.dump_png(f)

    def _checksum(self: Self, chunk_type: bytes, data: bytes) -> int:
        c = zlib.crc32(chunk_type)
        return zlib.crc32(data, c)

    def _gen_chunk(self: Self, chunk_type: bytes, data: bytes) -> bytes:
        ret = struct.pack('>I', len(data))
        ret += chunk_type
        ret += data
        ret += struct.pack('>I', self._checksum(chunk_type, data))
        return ret

    def _ihdr(_self: Self, width: int, height: int, bit_depth: int, color_type: ColorType) -> bytes:
        return struct.pack('>2I5B', width, height, bit_depth, color_type.value, 0, 0, 0)

    def _encode(_self: Self, img: Image) -> List[int]:

        ret = []

        for row in img:
            ret.append(0)
            ret.extend(value for pixel in row for value in pixel)

        return ret

    def _compress_data(_self: Self, data: List[int]) -> bytes:
        return zlib.compress(bytearray(data))

    def _idat(self: Self, img: Image) -> bytes:
        return self._compress_data(self._encode(img))


def test() -> None:

    img = Image(400,400)
    img.draw_rect(Vec2(400/2 - 200/2, 400/2 - 200/2), 200, 200, RED)
    img.draw_circle(Vec2(200, 200), 30, GREEN)
    img.draw_line(Vec2(400, 0), Vec2(0, 400), 6, BLUE)
    img.draw_triangle(Vec2(100, 300), Vec2(100, 200), Vec2(200, 300), PURPLE)
    png = PNG(img)
    png.save_png("foo.png")

if __name__ == "__main__":

    test()
