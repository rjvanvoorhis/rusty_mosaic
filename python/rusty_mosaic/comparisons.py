import typing
import numpy as np
import numpy.typing as npt

from rusty_mosaic import _lib


IndexArray = npt.NDArray[np.uint]
Float64Array = npt.NDArray[np.float64]
IntArray = npt.NDArray[np.int_]


class TileComparator(typing.Protocol):

    def __call__(
        self,
        image_blocks: typing.Union[IntArray, Float64Array],
        tiles: typing.Union[IntArray, Float64Array],
    ) -> npt.NDArray[np.uint]:
        """A function which finds the best tile for each corresponding region in the image

        Args:
            image_blocks (typing.Union[IntArray, Float64Array]): A list of flattended blocks that comprise an image
            tiles (typing.Union[IntArray, Float64Array]): A list of flattened tiles to replace the image blocks with

        Returns:
            npt.NDArray[np.uint]: A list of tile indexes. Each item in the list is the index in tiles that is the the most similar to the corresponding image block at that position
        """


euclid_distance_rust_i32 = _lib.find_best_tiles_i32
euclid_distance_rust_f64 = _lib.find_best_tiles_f64
