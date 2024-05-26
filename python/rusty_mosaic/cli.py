import time
import typing
import pathlib
import tempfile
import itertools

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


def make_keypress_callback(toggle: rusty_mosaic.utils.Toggle):
    def keypress_callback(value: str) -> bool:
        should_continue = value.lower() not in ["q", "quit", "x", "q!", " ", ""]
        toggle.value = should_continue
        return should_continue

    return keypress_callback


def show_text_gif(mosaic: rusty_mosaic.mosaic.TextGifMosaic) -> None:
    should_continue = rusty_mosaic.utils.Toggle(True)
    rusty_mosaic.utils.KeypressThread(callback=make_keypress_callback(should_continue))
    for frame_idx in itertools.cycle(range(len(mosaic.frames))):
        show_text_mosaic(mosaic.frames[frame_idx])
        typer.echo("Press enter to exit...")
        time.sleep(1.5 / mosaic.fps)
        if not should_continue:
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


@app.command()
def main(
    infile: pathlib.Path,
    scale: float = 1.0,
    tile_size: int = 8,
    text: bool = False,
    show: bool = False,
    outfile: typing.Optional[pathlib.Path] = None,
):
    if (show, outfile) == (False, None):
        raise ValueError("You must either show the mosaic or save it to a file")

    gif = is_gif(infile)
    cls, show_callback = {
        (False, False): (rusty_mosaic.mosaic.ImageMosaic, show_image_mosaic),
        (False, True): (rusty_mosaic.mosaic.GifMosaic, make_show_gif_mosaic(outfile)),
        (True, True): (
            rusty_mosaic.mosaic.TextGifMosaic,
            show_text_gif,
        ),
        (True, False): (rusty_mosaic.mosaic.TextMosaic, show_text_mosaic),
    }[(text, gif)]
    cls: rusty_mosaic.mosaic.Mosaic
    show_callback: ShowCallback
    mosaic = cls.load(infile, tile_size, scale=scale)
    tiles = rusty_mosaic.tile_library.TileLibrary.from_directory()
    mosaic.replace_tiles(tiles, inplace=True)
    if outfile:
        mosaic.save(outfile)

    if show:
        show_callback(mosaic)
