from setuptools import setup

setup(
    name='sofia_web',
    version='1.0.0',
    description='sofia web creates a simple web interface for users to interact with data outputs from the SoFiA-2 source finder',
    url='https://github.com/AusSRC/sofia_web',
    author='Austin Shen',
    author_email='austin.shen@csiro.au',
    packages=[
        "web",
    ],
    install_requires=[
        'django',
        'astropy',
        'astroquery',
        'python-dotenv'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'sofia_web=web.cli:main'
        ],
    },
)