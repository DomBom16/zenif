from setuptools import setup, find_packages

setup(
    name="flux",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "colorama==0.4.6"
        "setuptools==69.5.1"
        "wheel==0.43.0"
    ],
    author="DomBom16",
    description="A simple yet customizable and versatile library for logging messages to the console",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DomBom16/flux",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
