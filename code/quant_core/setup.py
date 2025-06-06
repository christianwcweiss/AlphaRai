from pathlib import Path

from setuptools import find_packages, setup

with open(Path(__file__).with_name("requirements.txt"), "r", encoding="utf-8") as file:
    install_requires = file.read().splitlines()

setup(
    name="quant_core",
    description="Central library for quant trading project",
    version="0.0.1",
    packages=find_packages(include=["*"]),
    package_data={"quant_core": ["py.typed"]},
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache License 2.0",
    ],
    license="Apache License 2.0",
    install_requires=install_requires,
    author="Christian Weiss",
    author_email="christian.wc.weiss@gmail.com",
)
