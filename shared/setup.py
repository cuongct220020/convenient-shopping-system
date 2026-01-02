from setuptools import setup, find_packages

setup(
    name='shopping-shared',
    version='0.1.0',
    packages=find_packages(),
    description='Common utilities for the convenient shopping system microservices.',
    author='Đặng Tiến Cường',
        author_email='cuong.dt@example.com',
    install_requires=[
        'sanic==24.12.0', # Match the version used in services
        'pydantic==2.10.6' # Match the version used in services
    ],
)
