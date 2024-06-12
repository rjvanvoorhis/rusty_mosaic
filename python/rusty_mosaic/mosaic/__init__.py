import typing
import pathlib

import numpy as np

from rusty_mosaic import comparisons
from rusty_mosaic import tile_library

from rusty_mosaic.mosaic.image_mosaic import ImageMosaic
from rusty_mosaic.mosaic.text_mosaic import TextMosaic
from rusty_mosaic.mosaic.gif_mosaic import GifMosaic
from rusty_mosaic.mosaic.text_gif_mosaic import TextGifMosaic


PathLike = typing.Union[str, pathlib.Path]


class Mosaic(typing.Protocol):

    @property
    def tile_data(self) -> np.ndarray:
        """Get the underlying image blocks"""
        ...

    def save(self, outfile: PathLike) -> None:
        """Save a representation of the mosaic to a file"""
        ...

    @classmethod
    def load(
        cls,
        filename: typing.Union[str, pathlib.Path],
        tile_size: int = 8,
        image_type: str = "L",
        scale: typing.Union[int, float] = 1,
        invert: bool = False,
        **kwargs: typing.Any,
    ) -> "Mosaic":
        """Initialize the mosaic from a file

        Args:
            filename (typing.Union[str, pathlib.Path]): A path to an image to mosaicfy
            tile_size (int, optional): The size of each image block. Defaults to 8.
            image_type (str, optional): An image mode. Defaults to "L".
            scale (typing.Union[int, float], optional): How much larger to make the resulting image. Defaults to 1.
        """
        ...

    def replace_tiles(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        inplace: bool = False,
    ) -> "Mosaic":
        """Replace the mosaic's tile data with those from the specified tile library

        Args:
            tiles (tile_library.TileLibrary): The tiles to replace the image blocks with
            cmp (comparisons.TileComparator, optional): A strategy to find the best tiles. Defaults to comparisons.euclid_distance_rust_i32.
            inplace (bool, optional): Create a new mosaic or modify the existing one. Defaults to False.

        Returns:
            Mosaic: A mosaic with the tiles replaced
        """
        ...


__all__ = ["Mosaic", "GifMosaic", "TextGifMosaic", "TextMosaic", "ImageMosaic"]
