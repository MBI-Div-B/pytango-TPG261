from setuptools import setup, find_packages

setup(
    name="tangods_tpg261",
    version="0.0.2",
    description="Tango device for Pfeiffer TPG261",
    author="Marin Borchert",
    author_email="",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["TPG261 = tangods_tpg261:main"]},
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pytango",
        "pyserial",
    ],
    url="https://github.com/MBI-Div-b/pytango-TPG261",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "TPG261",
    ],
)
