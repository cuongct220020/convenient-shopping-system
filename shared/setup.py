from setuptools import setup, find_packages

setup(
    name='shopping-shared',
    version='0.1.0',
    packages=find_packages(),
    description='Common utilities for the convenient shopping system microservices.',
    author='Đặng Tiến Cường',
    author_email='cuong.dt@example.com',
    install_requires=[
        'pydantic',
        'SQLAlchemy'
    ],
    extras_require={
        'fastapi': ['fastapi'],
        'sanic': ['sanic']
    }
)
