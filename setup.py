import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ConfReader",
    version="0.0.1",
    author="Pranav Kalariya",
    author_email="pranav.kalariya97@gmail.com",
    description=" Read .yaml, .cfg, .conf configuration file formats and generate a flat dictionary or write the configurations in .env, .json file or set the configurations in the os environment.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "ConfReader": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
