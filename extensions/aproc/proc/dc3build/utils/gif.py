import os
import shutil
import tempfile
from datetime import datetime

import xarray as xr
from PIL import Image, ImageDraw, ImageFont

from airs.core.models.model import Item, Role
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.dc3build.utils.overview import (
    create_overview, prepare_visualisation)

MAX_GIF_SIZE = 2048
FONT = "./assets/Roboto-Light.ttf"
FONT_ITALIC = "./assets/Roboto-LightItalic.ttf"
TEXT_COLOR = (0, 0, 0)


def truncate_datetime(times: list[datetime]) -> list[str]:
    """
    Finds the biggest common denominator of a list of times
    to get the shortest common representation
    """
    if any(t.second != times[0].second for t in times):
        return map(lambda t: t.__str__(), times)
    if any(t.minute != times[0].minute for t in times):
        return map(lambda t: t.__str__()[:-3], times)
    # Better to display minutes with hours
    if any(t.hour != times[0].hour for t in times):
        return map(lambda t: t.__str__()[:-3], times)
    if any(t.day != times[0].day for t in times):
        return map(lambda t: t.__str__()[:-9], times)
    if any(t.month != times[0].month for t in times):
        return map(lambda t: t.__str__()[:-12], times)
    return map(lambda t: str(t.year), times)


def add_text_on_image(imgPath: str, name: str,
                      description: str, bottom_text: str):

    def get_text_size(text: str, font):
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return text_width, text_height

    img = Image.open(imgPath)
    band_height = img.height // 10
    description_band_height = (1 if description else 0) * img.height // 20

    font = ImageFont.truetype(FONT, int(band_height * 0.6))
    # TODO: change font based on description length and/or split text
    small_font = ImageFont.truetype(FONT_ITALIC, int(band_height * 0.6 * 0.3))

    # Add white bands to the preview
    # Top band + bottom band + description band
    img_total_height = img.height + 2 * band_height + description_band_height
    img_band = Image.new("RGB", (img.width, img_total_height), "White")
    img_band.paste(img, (0, band_height + description_band_height))

    # Create an editable object of the image
    img_edit = ImageDraw.Draw(img_band)

    # Add centered text in the top white band

    name_pos = ((img.width - get_text_size(name, font)[0]) / 2,
                (band_height - get_text_size(name, font)[1]) / 2)
    img_edit.text(name_pos, name, TEXT_COLOR, font=font)

    if description:
        description_pos = ((img.width - get_text_size(description, font)[0]) / 2,
                           band_height + (description_band_height -
                                          get_text_size(description, font)[1]) / 2)
        img_edit.text(description_pos, description,
                      TEXT_COLOR, font=small_font)

    # Add centered text in the bottom white band
    bottom_text_pos = ((img.width - get_text_size(bottom_text, font)[0]) / 2,
                       img_total_height - band_height + (
                            band_height - get_text_size(bottom_text, font)[1]) / 2)
    img_edit.text(bottom_text_pos, bottom_text, TEXT_COLOR, font=font)

    # Add the credits
    credits = "Powered by ARLAS (Gisaïa)"
    credits_pos = (img.width - get_text_size(credits, small_font)[0],
                   img_total_height - get_text_size(credits, small_font)[1])
    img_edit.text(credits_pos, credits, TEXT_COLOR, font=small_font)

    img_band.save(imgPath)


def create_gif(datacube: xr.Dataset, item: Item, gif_path: str):
    """
    Create a gif based on a datacube and its item
    """
    size = get_gif_size(datacube)

    cube_asset = item.assets[Role.datacube.value]
    # Find where to put the temporary pictures
    working_dir = tempfile.mkdtemp(dir=AccessManager.tmp_dir, prefix="{}_{}".format("overview", cube_asset.title.replace(" ", "_")))

    times = list(map(lambda t: datetime.fromtimestamp(t), datacube.t.values))

    # Normalize all slices the same way to have more meaningful gifs
    coarsed_datacube, clip_values = prepare_visualisation(
        datacube, list(item.properties.dc3__overview.values()), size)

    # Generate the pictures for the gif
    for t_text, t in zip(truncate_datetime(times), datacube.t.values):
        img_path = os.path.join(working_dir, f"{t}.png")
        create_overview(coarsed_datacube, item.properties.dc3__overview, img_path, clip_values)

        add_text_on_image(img_path, cube_asset.title,
                          cube_asset.description, t_text)

    # Create the gif and clean-up
    os.system(f"cd {working_dir};" +
              f"convert -delay 100 -loop 0 *.png {gif_path}")
    shutil.rmtree(working_dir)  # !DELETE!


def get_gif_size(datacube: xr.Dataset,
                 max_gif_size=MAX_GIF_SIZE) -> tuple[int, int]:
    """
    Returns the [length, width] in pixels of the gif to generate
    """
    if len(datacube.x) <= max_gif_size and len(datacube.y) <= max_gif_size:
        return len(datacube.x), len(datacube.y)
    else:
        if len(datacube.x) <= len(datacube.y):
            return [max_gif_size,
                    int(len(datacube.y) * max_gif_size / len(datacube.x))]
        return int(len(datacube.x) * max_gif_size / len(datacube.y)), max_gif_size
