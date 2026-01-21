import setuptools


def get_requirements():
    with open("requirements.aias_common.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aias_common",
    version=aias_version,
    author="Gisaïa",
    description="ARLAS AIAS common library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.10',
    package_dir={'': 'src'},
    install_requires=get_requirements()
)
