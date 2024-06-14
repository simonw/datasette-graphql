from setuptools import setup
import os

VERSION = "3.0a0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-graphql",
    description="Datasette plugin providing an automatic GraphQL API for your SQLite databases",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-graphql",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-graphql/issues",
        "CI": "https://github.com/simonw/datasette-graphql/actions",
        "Changelog": "https://github.com/simonw/datasette-graphql/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_graphql"],
    entry_points={"datasette": ["graphql = datasette_graphql"]},
    install_requires=[
        "datasette>=1.0a5",
        "graphene>=3.1.0,<4.0",
        "graphql-core>=3.2.1",
        "sqlite-utils",
    ],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    package_data={
        "datasette_graphql": ["templates/*.html", "static/*.js", "static/*.css"]
    },
)
