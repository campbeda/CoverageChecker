import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coveragecheck",
    version="0.0.1",
    author="Jeff Nelson, Dave Campbell, and Colton Saska",
    author_email="jdn5126@gmail.com dncswim76@gmail.com colt.saska@gmail.com",
    description="Set of tools for validating code coverage as a merge criterion in a CI pipeline.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jdn5126/CoverageChecker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['coverage'],
    entry_points={
        'console_scripts': [
            'coveragecheck = coveragecheck.coveragecheck:main',
        ],
    }
)

