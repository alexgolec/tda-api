import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tda-api',
    version='0.0.1',
    author='Alex Golec',
    author_email='bottomless.septic.tank@gmail.com',
    description='An unofficial wrapper around the TD Ameritrade HTTP API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/alexgolec/tda-api',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

