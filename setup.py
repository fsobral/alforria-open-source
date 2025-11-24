import setuptools

# Long description of the project
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="alforria", # Replace with your own username
    version="1.0.0",
    author="FNC Sobral",
    author_email="fncsobral@uem.br",
    description="Teacher Scheduler tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alforria",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
