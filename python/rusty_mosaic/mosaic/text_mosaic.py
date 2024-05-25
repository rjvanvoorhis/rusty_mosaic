import typing
import string
import pathlib
import dataclasses
import numpy as np

import numpy.typing as npt

from rusty_mosaic import tile_library
from rusty_mosaic import comparisons
from rusty_mosaic.mosaic.image_mosaic import ImageMosaic

ASCII_TILE_TEXT_MAP = np.asarray(
    list(f"{string.ascii_letters}0123456789_-+[]{{}}\\|/,.:;'\"!@#$%^&*?><~` ")
)


@dataclasses.dataclass
class TextMosaic:
    tile_data: npt.NDArray[np.str_]
    text_map: npt.NDArray[np.str_]
    image_mosaic: ImageMosaic

    @classmethod
    def load(
        cls,
        filename: typing.Union[str, pathlib.Path],
        tile_size: int = 8,
        image_type: str = "L",
        scale: typing.Union[int, float] = 1,
        text_map: npt.NDArray[np.str_] = ASCII_TILE_TEXT_MAP,
    ) -> "TextMosaic":
        image_mosaic = ImageMosaic.load(filename, tile_size, image_type, scale)
        tile_data = np.full(image_mosaic.tile_data.shape[0], " ")
        return cls(tile_data=tile_data, text_map=text_map, image_mosaic=image_mosaic)

    def save(self, outfile: typing.Union[str, pathlib.Path]) -> None:
        pathlib.Path(outfile).write_text(self.text)

    @property
    def text(self):
        return "\n".join(
            "".join(row) for row in self.tile_data.reshape(self.image_mosaic.rows, -1)
        )

    def replace_tiles(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        inplace: bool = False,
    ):
        if tiles.tile_data.shape[0] > self.text_map.shape[0]:
            raise ValueError(
                f"The provided tile library has {tiles.shape[0]} tiles but the current text map only has {self.text_map.size} characters"
            )

        best = cmp(self.image_mosaic.tile_data, tiles.tile_data)
        if inplace:
            self.tile_data = self.text_map[best]
            return self

        return type(self)(
            tile_data=self.text_map[best],
            text_map=self.text_map,
            image_mosaic=self.image_mosaic,
        )
