import setuptools

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('tda/version.py', 'r') as f:
    '''Version looks like `version = '1.2.3'`'''
    version = [s.strip() for s in f.read().strip().split('=')][1]
    version = version[1:-1]

setuptools.setup(
    name='tda-api',
    version=version,
    author='Alex Golec',
    author_email='bottomless.septic.tank@gmail.com',
    description='An unofficial wrapper around the TD Ameritrade HTTP API.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/alexgolec/tda-api',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests_oauthlib',
        'python-dateutil',
        'selenium', 
        'websockets'],
    keywords='finance trading equities bonds options research',
    project_urls={
        'Documentation': 'https://tda-api.readthedocs.io/en/latest/',
        'Source': 'https://github.com/alexgolec/tda-api',
        'Tracker': 'https://github.com/alexgolec/tda-api/issues',
    },
    license='MIT',
)

