from setuptools import setup, find_packages

setup(
    name="jarvis",
    version="0.0.0",
    description="Jarvis project",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">3.10",
    include_package_data=True,
    install_requires=[],
    entry_points={"console_scripts": ["jarvis=Jarvis.main:main"]},
)
