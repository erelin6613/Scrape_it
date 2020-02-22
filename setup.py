import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrape_it-erelin6613",
    version="0.1.7",
    author="Valentyna Fihurska",
    author_email="valentineburn@gmail.com",
    description="Systemitized tool for scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erelin6613/Scrape_it/releases/tag/v0.1.7",
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
    python_requires='>=3.5',
)
