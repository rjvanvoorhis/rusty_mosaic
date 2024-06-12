import time
import typing
import pathlib
import tempfile
import itertools
import enum

import typer
import rusty_mosaic
import subprocess

app = typer.Typer()


ShowCallback = typing.Callable[[rusty_mosaic.mosaic.Mosaic], None]


def show_gif(filename: str) -> None:
    subprocess.call(["open", "-a", "firefox", filename])


def make_show_gif_mosaic(outfile: typing.Optional[pathlib.Path] = None):
    def show_gif_mosaic(mosaic: rusty_mosaic.mosaic.Mosaic) -> None:
        if outfile is not None:
            return show_gif(str(outfile))

        with tempfile.NamedTemporaryFile(suffix=".gif") as tmp:
            mosaic.save(tmp.name)
            show_gif(tmp.name)
            input("Press any button to continue...")

        return None

    return show_gif_mosaic


def show_text_gif(mosaic: rusty_mosaic.mosaic.TextGifMosaic) -> None:
    counter = {"value": 0}

    def should_continue():
        return counter["value"] <= 0

    def should_continue_callback(_: str) -> bool:
        counter["value"] += 1
        return should_continue()

    rusty_mosaic.utils.KeypressThread(callback=should_continue_callback)
    for frame_idx in itertools.cycle(range(len(mosaic.frames))):
        show_text_mosaic(mosaic.frames[frame_idx])
        typer.echo("Press enter to exit...")
        time.sleep(1.5 / mosaic.fps)
        if not should_continue():
            break
        typer.clear()


def show_image_mosaic(
    mosaic: rusty_mosaic.mosaic.ImageMosaic,
):
    mosaic.image.show()


def show_text_mosaic(
    mosaic: rusty_mosaic.mosaic.TextMosaic,
):
    typer.echo(mosaic.text)


def is_gif(infile: pathlib.Path) -> bool:
    return pathlib.Path(infile).suffix.lower().endswith("gif")


class ImageMode(str, enum.Enum):
    color = "RGB"
    grayscale = "L"


@app.command()
def main(
    infile: pathlib.Path,
    scale: float = 1.0,
    tile_size: int = 8,
    text: bool = False,
    show: bool = False,
    invert: bool = False,
    mode: ImageMode = ImageMode.grayscale,
    outfile: typing.Optional[pathlib.Path] = None,
    tile_directory: pathlib.Path = rusty_mosaic.tile_library.ASCII_TILES,
):
    if (show, outfile) == (False, None):
        raise ValueError("You must either show the mosaic or save it to a file")

    gif = is_gif(infile)
    callback_map: typing.Dict[
        typing.Tuple[bool, bool], typing.Tuple[typing.Any, typing.Callable]
    ] = {
        (False, False): (rusty_mosaic.mosaic.ImageMosaic, show_image_mosaic),
        (False, True): (rusty_mosaic.mosaic.GifMosaic, make_show_gif_mosaic(outfile)),
        (True, True): (
            rusty_mosaic.mosaic.TextGifMosaic,
            show_text_gif,
        ),
        (True, False): (rusty_mosaic.mosaic.TextMosaic, show_text_mosaic),
    }
    cls, show_callback = callback_map[(text, gif)]
    cls: rusty_mosaic.mosaic.Mosaic
    show_callback: ShowCallback
    mosaic = cls.load(infile, tile_size, scale=scale, invert=invert, image_type=mode)
    tiles = rusty_mosaic.tile_library.TileLibrary.from_directory(
        tile_directory, tile_size=tile_size, image_type=mode
    )
    cmp = (
        rusty_mosaic.comparisons.euclid_distance_rust_i32
        if gif
        else rusty_mosaic.comparisons.parallel_euclid_distance_rust_i32
    )
    mosaic.replace_tiles(tiles, inplace=True, cmp=cmp)
    if outfile:
        mosaic.save(outfile)

    if show:
        show_callback(mosaic)
