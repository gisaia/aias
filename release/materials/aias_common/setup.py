
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aias_common",
    version=aias_version,
    author="Gisaïa",
    description="ARLAS AIAS common library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    py_modules=["aias_common.access.storages.abstract",
                "aias_common.access.storages.https",
                "aias_common.access.storages.file",
                "aias_common.access.storages.utils",
                "aias_common.access.storages.http",
                "aias_common.access.storages.gs",
                "aias_common.access.configuration",
                "aias_common.access.manager",
                "aias_common.logger",
                "aias_common.rest.exception",
                "aias_common.rest.healthcheck",
                "aias_common.rest.exception_handler"],
    package_dir={'': 'src'},
    install_requires=[]
)
