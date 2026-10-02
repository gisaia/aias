from airs.core.models.model import Band


BLUE_BAND = 470
GREEN_BAND = 550
RED_BAND = 660


def find_rgb_bands(bands: list[Band]):
    def update_closest_band(band: Band, target_wavelength: float, closest_band):

        if closest_band is None:
            closest_band = {"idx": band.index, "wavelength": band.eo__center_wavelength}
        elif abs(band.eo__center_wavelength - target_wavelength) < abs(closest_band["wavelength"] - target_wavelength):
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
