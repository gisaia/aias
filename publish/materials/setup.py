
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aeoprsmodel",
    version=aeoprsmodel_version,                        
    author="Gisaïa",                     
    description="ARLAS Earth Observation Product Registration Service Model",
    long_description=long_description,      
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    
    python_requires='>=3.11',     
    py_modules=["aeoprs.core.models.model","aeoprs.core.models.mapper"],  
    package_dir={'':'src'},
    install_requires=[]
)
