import typing
from PIL import Image


def resize_image(
    image: Image.Image, target_size: typing.Tuple[int, int]
) -> Image.Image:
    if target_size == image.size:
        return image

    return image.resize(target_size, Image.Resampling.LANCZOS)


def scale_image(image: Image.Image, scale: typing.Union[int, float]) -> Image.Image:
    if scale <= 0:
        raise ValueError("Scaling factor must be non-zero")
    return resize_image(
        image, tuple(int(dimension * scale) for dimension in image.size)
    )


def crop_largest_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    minimum_dim = min(image.size)
    width_crop = width - minimum_dim
    height_crop = height - minimum_dim
    return image.crop(
        (
            width_crop // 2,
            height_crop // 2,
            (width - width_crop) + (width_crop // 2),
            (height - height_crop) + (height_crop // 2),
        )
    )


def crop_tile(image: Image.Image, tile_size: int) -> Image.Image:
    width, height = image.size
    width_crop, height_crop = (dim % tile_size for dim in image.size)
    if not any((width_crop, height_crop)):
        return image
    return image.crop(
        (
            width_crop // 2,
            height_crop // 2,
            (width - width_crop) + (width_crop // 2),
            (height - height_crop) + (height_crop // 2),
        )
    )
