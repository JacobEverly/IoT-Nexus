from setuptools import setup, find_packages
from py_cc import VERSION

setup(
    name='Compact Certificate',
    version=VERSION,
    url='https://github.com/JacobEverly/Independent-Research-Spring-2023',
    author='Jacob Everly, Hau Chu',
    author_email='je354@cornell.edu, hc793@cornell.edu',
    description='Reference implementation in Python of Compact Certificate',
    packages=find_packages(exclude=['tests', 'docs']),
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.9',
    install_requires=[
        'pytest~=7.1.3',
        'galois~=0.0.30',
        'numpy~=1.22.4',
        'setuptools>=42.0',
        'py_ecc~=6.0.0',
    ],
    keywords=['Compact Certificate', 'Zero Knowledge'],
)