from setuptools import setup, find_packages

setup(
    name='flutter_unused',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'rich',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'flutter_unused = flutter_unused.__main__:main',
        ],
    },
)
