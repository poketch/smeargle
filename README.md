# Smeargle 

Single file Python library for creating PNG images

## Usage 

> proj-dir
```bash
wget https://raw.githubusercontent.com/poketch/smeargle/master/smeargle.py
```

> main.py
```python 
import functools
from smeargle import Image, PNG, Pixel
from smeargle import BLACK, WHITE

def checker_board(block_size: int, x: int, y: int) -> Pixel:
    if ((x // block_size) + (y//block_size)) % 2 == 0:
        return WHITE
    else:
        return BLACK

img = Image.from_generator(800, 800, functools.partial(checker_board, 100))
png = PNG(img)
png.save_png("foo.png")
```

