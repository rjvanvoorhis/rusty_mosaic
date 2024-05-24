import typing
import string
import pathlib
import dataclasses

from PIL import Image
import numpy as np


from rusty_mosaic import utils

ASCII_TILES = pathlib.Path(__file__).parent / "__assets__" / "ascii_tiles"
ASCII_TILE_TEXT = list(
    f"{string.ascii_letters}0123456789_-+[]{{}}\\|/,.:;'\"!@#$%^&*?><~` "
)


@dataclasses.dataclass
class TileLibrary:

    tile_size: int
    tile_data: np.ndarray

    @staticmethod
    def _process_tile(
        tile_path: str, tile_size: int, image_type: str = "L"
    ) -> np.ndarray:
        print(f"tile_path = {pathlib.Path(tile_path).name}")
        with Image.open(tile_path) as image:
            image = utils.crop_largest_square(image)
            image = utils.resize_image(image, (tile_size, tile_size))
            data = np.asarray(image.convert(image_type)).flatten()
        return data

    @classmethod
    def from_directory(
        cls,
        path: typing.Union[str, pathlib.Path] = ASCII_TILES,
        tile_size: int = 8,
        image_type: str = "L",
    ) -> "TileLibrary":
        return cls(
            tile_size=tile_size,
            tile_data=np.asarray(
                [
                    cls._process_tile((image_path.absolute()), tile_size, image_type)
                    for image_path in sorted(pathlib.Path(path).glob("*"))
                ]
            ),
        )
