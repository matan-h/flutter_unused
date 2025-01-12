from setuptools import setup, find_packages

setup(
    name='unused_analyzer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'unused_analyzer = unused_analyzer.__main__:main',
        ],
    },
)
