import setuptools


with open("README.md", encoding="utf-8") as file_:
    long_description = file_.read()


setuptools.setup(
    name="whilelang",
    version="0.0.1",
    author="Bottersnike",
    author_email="bottersnike237@gmail.com",
    description="A minimal implementation of the While language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bottersnike/whileland",
    project_urls={
        "Bug Tracker": "https://github.com/Bottersnike/whileland/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    scripts=[
        "scripts/while.py"
    ],
    packages=["whilelang"],
    python_requires=">=3.8",
)
