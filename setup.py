from setuptools import setup, find_packages

setup(
    name="fluxutils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["colorama==0.4.6", "wheel==0.43.0"],  # Add any dependencies here
    author="Domenic Urso",
    author_email="domenicjurso@gmail.com",
    description="CLI tools to make your programs run smoother",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DomBom16/flux",  # Update this URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
