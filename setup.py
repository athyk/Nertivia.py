import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


requirements: list = ["setuptools", "requests", "nest_asyncio", "six>=1.9.0", "websocket-client>=0.54.0",
                      "websockets>=7.0", "aiohttp>=3.4", "bidict"]

setuptools.setup(
    name='nertivia',  # How you named your package folder (MyLib)
    version='0.2.8',  # Start with a small number and increase it with every change you make
    license='apache-2.0',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Python API Wrapper for Nertivia to make bots',  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nertivia-PY/Nertivia.py/",
    author='FluxedScript',  # Type in your name
    keywords=['API Wrapper', 'SIMPLE', 'PYTHON', "nertivia"],  # Keywords that define your package best
    package_dir={"socketioN": "socketioN"},
    packages=setuptools.find_namespace_packages(include=['nertivia', "socketioN", "engineioN"]),
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
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
    ],
    python_requires=">=3.6",
)
