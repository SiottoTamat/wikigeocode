from setuptools import setup, find_packages

setup(
    name="wikigeocode",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "wikipedia",
        "wikipedia-api",
    ],  # add dependencies here
)
