from setuptools import setup, find_packages

install_requires = [
    "fastapi==0.104.1",
    "fastapi-login==1.9.1",
    "SQLAlchemy==2.0.23",
    "pydicom==2.4.3",
    "python-multipart==0.0.6"
]

setup(
    name='takehome',
    version='0.1.0',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires,
    tests_require=[
        'pytest',
    ],
)
