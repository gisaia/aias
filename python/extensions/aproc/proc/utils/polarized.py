from pydantic import BaseModel, Field, computed_field


class PolarizedAsset(BaseModel):
    polarization: str = Field()
    path: str = Field()
    name: str = Field()
    metadata: str | None = Field(default=None)

    @computed_field
    @property
    def description(self) -> str:
        return f"Polarization {self.polarization}"


class DriverWithPolarizedAssets:

    def add_measurement(self, measurements: list[PolarizedAsset], polarization: str, path: str, name: str | None = None, metadata: str | None = None):
        measurements.append(PolarizedAsset(
            polarization=polarization.upper(),
            path=path,
            name=name or f"{polarization.upper()}_data",
            metadata=metadata))

    def pick_data_asset(self, measurements: list[PolarizedAsset]) -> PolarizedAsset | None:
        """
        Picks the data asset for a radar archive with HH, VV, HV, VH polarizations
        """
        # The first polarization found in the following order will be selected as the data asset
        for polarization in ["HH", "VV", "HV", "VH"]:
            result = [pol for pol in measurements if pol.polarization == polarization]
            if len(result) > 0:
                return result[0]
        return None
