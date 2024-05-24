import typing
import pathlib
import dataclasses

from PIL import Image
import numpy as np


from rusty_mosaic import utils
from rusty_mosaic import comparisons
from rusty_mosaic import tile_library


@dataclasses.dataclass
class Mosaic:
    MAX_SIZE: typing.ClassVar[int] = 4_000

    tile_data: np.ndarray
    tile_size: int
    rows: int

    @staticmethod
    def _image_to_blocks(image: Image.Image, tile_size: int) -> np.ndarray:
        data = np.asarray(image)
        height, width, channels = [*data.shape, 1][:3]
        rows = height // tile_size
        cols = width // tile_size
        return np.asarray(
            [np.split(row, cols, axis=1) for row in np.split(data, rows)]
        ).reshape(rows * cols, tile_size * tile_size * channels)

    @staticmethod
    def _blocks_to_image(blocks: np.ndarray, tile_size: int, rows: int) -> Image.Image:
        channels = blocks.shape[1] / (tile_size * tile_size)
        if channels == 1:
            blocks = blocks.reshape(rows, -1, tile_size, tile_size)
        else:
            blocks = blocks.reshape(rows, -1, tile_size, tile_size, channels)

        pix_map = np.concatenate(
            [np.concatenate(block, axis=1) for block in blocks], axis=0
        )
        return Image.fromarray(pix_map.astype(np.uint8))

    @classmethod
    def from_image(cls, image: Image.Image, tile_size: int) -> "Mosaic":
        image = utils.crop_tile(image, tile_size)
        tile_data = cls._image_to_blocks(image, tile_size)
        rows = image.size[1] // tile_size
        return cls(tile_size=tile_size, tile_data=tile_data, rows=rows)

    @property
    def image(self) -> Image.Image:
        return self._blocks_to_image(self.tile_data, self.tile_size, self.rows)

    def save(self, outfile: typing.Union[str, pathlib.Path]):
        image = self.image
        if any(dim > self.MAX_SIZE for dim in image.size):
            image = image.copy()
            image.thumbnail((self.MAX_SIZE, self.MAX_SIZE), Image.Resampling.LANCZOS)
        image.save(str(outfile))

    @classmethod
    def load(
        cls,
        filename: typing.Union[str, pathlib.Path],
        tile_size: int = 8,
        image_type: str = "L",
        scale: typing.Union[int, float] = 1,
    ):
        filename = str(filename)
        with Image.open(filename) as image:
            image.format = filename.split(".")[-1] if not image.format else image.format
            image = image.convert(image_type)
            inst = cls.from_image(utils.scale_image(image, scale), tile_size)
        return inst

    def replace_tiles(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        inplace: bool = False,
    ) -> "Mosaic":
        best = cmp(self.tile_data, tiles.tile_data)
        if inplace:
            self.tile_data = tiles.tile_data[best]
            return self

        tile_data = tiles.tile_data[best]
        return type(self)(tile_data, self.tile_size, self.rows)

    def to_text(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        text_bank: str = tile_library.ASCII_TILE_TEXT,
    ) -> str:
        best = cmp(self.tile_data, tiles.tile_data)
        text = np.asarray(text_bank)[best].reshape(self.rows, -1)
        return "\n".join("".join(row) for row in text)
