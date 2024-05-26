import typing
import dataclasses
import pathlib

import numpy as np
import imageio.v3 as iio
from PIL import Image
from concurrent import futures

from rusty_mosaic import utils
from rusty_mosaic import mosaic
from rusty_mosaic import comparisons
from rusty_mosaic import tile_library


@dataclasses.dataclass
class TextGifMosaic:
    frames: typing.List[mosaic.TextMosaic]
    fps: int

    @property
    def tile_data(self) -> np.ndarray:
        return np.asarray([frame.text for frame in self.frames])

    def save(self, outfile: typing.Union[str, pathlib.Path]):
        outfile = pathlib.Path(outfile)
        if outfile.exists() and not outfile.is_dir():
            raise ValueError(f"{outfile} is not a directory")
        outfile.mkdir(parents=True, exist_ok=True)
        frame_padding = len(str(len(self.frames))) + 1
        for idx, frame in enumerate(self.frames):
            frame.save(outfile / f"frame-{idx:0{frame_padding}}.txt")

    @classmethod
    def load(
        cls,
        filename: typing.Union[str, pathlib.Path],
        tile_size: int = 8,
        image_type: str = "L",
        scale: typing.Union[int, float] = 1,
    ) -> "TextGifMosaic":
        metadata = iio.immeta(filename)
        frames = iio.imread(filename)
        fps = (
            metadata.get("fps")
            or int(frames.shape[0] / metadata.get("duration", 1_000_000_000))
            or 60
        )
        mosaics = [
            mosaic.TextMosaic.from_image(
                utils.scale_image(Image.fromarray(image).convert(image_type), scale),
                tile_size=tile_size,
            )
            for image in frames
        ]

        return cls(frames=mosaics, fps=fps)

    def replace_tiles(
        self,
        tiles: tile_library.TileLibrary,
        cmp: comparisons.TileComparator = comparisons.euclid_distance_rust_i32,
        inplace: bool = False,
    ) -> "TextGifMosaic":
        executor = futures.ProcessPoolExecutor()
        jobs = [
            executor.submit(mosaic.replace_tiles, tiles, cmp, inplace=True)
            for mosaic in self.frames
        ]
        frames = [future.result() for future in jobs]
        if inplace:
            self.frames = frames
            return self
        return type(self)(frames=frames, fps=self.fps)
