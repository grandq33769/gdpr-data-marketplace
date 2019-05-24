from setuptools import setup

setup(
    name='data_marketplace',
    packages=['data_marketplace'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_socketio'
    ],
)