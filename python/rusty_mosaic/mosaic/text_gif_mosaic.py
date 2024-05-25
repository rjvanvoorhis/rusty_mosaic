import typing
import dataclasses
import pathlib

import numpy as np

from rusty_mosaic import comparisons
from rusty_mosaic import tile_library

MSG = "This method is not yet implemetned"


@dataclasses.dataclass
class TextGifMosaic:
    tile_data: np.ndarray

    def save(self, outfile: typing.Union[str, pathlib.Path]):
        raise NotImplementedError(MSG)

    @classmethod
    def load(
        cls,
        filename: typing.Union[str, pathlib.Path],
        tile_size: int = 8,
        image_type: str = "L",
        scale: typing.Union[int, float] = 1,
    ) -> "TextGifMosaic":
        raise NotImplementedError(MSG)

    def replace_tiles(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        inplace: bool = False,
    ) -> "TextGifMosaic":
        raise NotImplementedError(MSG)
