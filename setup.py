from setuptools import setup, find_packages

setup(
    name="tangods_tpg26x",
    version="0.0.1",
    description="Tango device for Pfeiffer TPG26x",
    author="Marin Borchert",
    author_email="",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["TPG26xTango = tangods_tpg26x:main"]},
    license="MIT",
    packages=["tangods_tpg26x"],
    install_requires=[
        "pytango",
        "numpy",
        "pyserial",
    ],
    url="https://github.com/MBI-Div-b/pytango-TPG26x",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "TPG26x",
    ],
)
