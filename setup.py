from setuptools import setup, find_packages
import os
AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")

setup(
    name="airs",
    version=AIAS_VERSION,
    packages=find_packages(),
)
