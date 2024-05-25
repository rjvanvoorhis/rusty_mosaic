import typing
import pathlib

import typer

import rusty_mosaic

app = typer.Typer()


ShowCallback = typing.Callable[[rusty_mosaic.mosaic.Mosaic], None]


def show_gif_mosaic(
    mosaic: rusty_mosaic.mosaic.Mosaic,
):
    raise NotImplementedError("This mosaic has not been implemented")


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
        (False, True): (rusty_mosaic.mosaic.GifMosaic, show_gif_mosaic),
        (True, True): (rusty_mosaic.mosaic.TextGifMosaic, show_gif_mosaic),
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
