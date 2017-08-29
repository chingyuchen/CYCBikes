'''
Create cycbikes package
Copyright (c) 2017 Ching-Yu Chen
'''
from setuptools import setup

setup(
    name="cycbikes",
    version="1.0",
    author="Ching-Yu Chen",
    author_email="chingyuc.cyc@gmail.com",
    maintainer='Ching-Yu Chen',
    maintainer_email='chingyuc.cyc@gmail.com',
    packages=["cycbikes"],
    license="LICENSE",
    description="A telegram bot provides real-time information of worldwide bike-share system.",
    long_description=open('README.md').read(),
    install_requires=[
        'telepot>=12.1',
        'pyTelegramBotAPI>=3.2.0',
        'geocoder>=1.24.1',
        'geopy>=1.11.0',
    ],
    scripts=['cycbikes'],
)