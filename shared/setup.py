from setuptools import setup, find_packages

setup(
    name='shopping-shared',
    version='0.1.0',
    packages=find_packages(),
    description='Common utilities for the convenient shopping system microservices.',
    author='Đặng Tiến Cường',
    author_email='cuong.dt@example.com',
    install_requires=[
        'SQLAlchemy==2.0.43',
        'pydantic==2.11.9',
        'pydantic-settings==2.11.0',
        'aiokafka==0.12.0',
        'async-timeout==5.0.1'
    ],
    extras_require={
        'fastapi': [
            'fastapi==0.118.0',
            'anyio==4.11.0',
            'starlette==0.48.0',
            'greenlet==3.2.4',
            'idna==3.10',
            'psycopg2-binary==2.9.10'
        ],
        'sanic': [
            'sanic==24.12.0'
        ]
    }
)
