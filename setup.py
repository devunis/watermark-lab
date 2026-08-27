"""Legacy editable-install bridge for older pip/setuptools environments."""

from setuptools import find_packages, setup


setup(
    name="watermark-lab",
    version="0.1.0",
    packages=find_packages(include=["watermark_lab", "watermark_lab.*"]),
)
