import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements: list = f.read().splitlines()
print(requirements)
setuptools.setup(
    name='pna',  # How you named your package folder (MyLib)
    version='0.0.1',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Python API Wrapper for Nertivia to make bots',  # Give a short description about your library
    long_description=long_description,
    long_description_content_type ="text/markdown",
    author='FluxedScript',  # Type in your name
    keywords=['API Wrapper', 'SIMPLE', 'PYTHON', "nertivia"],  # Keywords that define your package best
    package_dir={"socketioN": "socketioN"},
    packages=setuptools.find_namespace_packages(include=['nertivia', "socketioN"]),
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
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
    ],
    python_requires=">=3.6",
)
