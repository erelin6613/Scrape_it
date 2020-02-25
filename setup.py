import setuptools
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrape_it",
    DATA_DIR = os.path.join(sys.prefix, 
		"local/lib/python3.6/dist-packages", "scrape_it"),
    version="0.3.6",
    py_modules=["scrape_it"],
    author="Valentyna Fihurska",
    author_email="valentineburn@gmail.com",
    description="Systemitized tool for scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erelin6613/Scrape_it",
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
    install_requires=["requests", "tqdm", "numpy", "nltk",
			"address-parser", "beautifulsoup4",
			"bs4", "lxml", "nltk", 
			"phonenumbers", "pyap", "regex",
			"selenium", "tldextract"],
    python_requires='>=3.5',
)
