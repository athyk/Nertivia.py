import setuptools

with open("README2.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements: list = ["setuptools", "requests", "nest_asyncio", "six>=1.9.0", "websocket-client>=0.54.0",
                      "websockets>=7.0", "aiohttp>=3.4", "bidict"]

setuptools.setup(
    name='nertivia',  # How you named your package folder (MyLib)
    version='0.2.92',  # Start with a small number and increase it with every change you make
    license='apache-2.0',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='A mirror package for nertivia.py. Please install that instead.',  # Give a short description about
    # your library
    long_description= long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nertivia-PY/Nertivia.py/",
    author='Athy K',  # Type in your name
    keywords=['API Wrapper', 'SIMPLE', 'PYTHON'],  # Keywords that define your package best
    packages=setuptools.find_namespace_packages(include=['nertivia']),
    install_requires=requirements,
    extras_require={
        'client': [
            'requests>=2.21.0',
            'websocket-client>=0.54.0',
        ],
        'asyncio_client': [
            'aiohttp>=3.4',
            'websockets>=7.0',
        ]
    },
    python_requires=">=3.6",
)
