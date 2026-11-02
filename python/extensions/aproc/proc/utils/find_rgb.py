from airs.core.models.model import Band
from aproc.core.logger import Logger

LOGGER = Logger.get_logger()

# Wavelengths in eo__bands are in µm
BLUE_BAND = 0.470
GREEN_BAND = 0.550
RED_BAND = 0.660


def find_rgb_bands(bands: list[Band]):
    # If less than 3 bands have an index and a central wavelength, then take the first band
    if len([band for band in bands if band.index is not None and band.eo__center_wavelength is not None]) < 3:
        LOGGER.warn("Not enough bands have an index and a center wavelength. Using the first band only")
        return [1]

    def update_closest_band(band: Band, target_wavelength: float, closest_band):
        # Skip the band if the necessary parameters are not defined
        if band.eo__center_wavelength is None or band.index is None:
            return closest_band

        if closest_band is None or abs(band.eo__center_wavelength - target_wavelength) < abs(closest_band["wavelength"] - target_wavelength):
            closest_band = {"idx": band.index, "wavelength": band.eo__center_wavelength}
        return closest_band

    closest_blue_band = None
    closest_green_band = None
    closest_red_band = None

    for band in bands:
        closest_blue_band = update_closest_band(band, BLUE_BAND, closest_blue_band)
        closest_green_band = update_closest_band(band, GREEN_BAND, closest_green_band)
        closest_red_band = update_closest_band(band, RED_BAND, closest_red_band)

    return [closest_red_band["idx"], closest_green_band["idx"], closest_blue_band["idx"]]
