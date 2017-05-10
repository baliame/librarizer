from setuptools import *

description = 'Command line tool to organize scene TV episodes into a library readable by XMBC and Kodi (and easier on the eye!). The developer of this tool does not condone illegally downloading TV series in regions where it is applicable, please only use this on legally obtained TV episodes.'

setup(
    name='librarizer',
    version='1.0.0rc1',
    description=description,
    long_description=description,
    url='https://github.com/baliame/librarizer',
    author='Baliame',
    author_email='akos.toth@cheppers.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    keywords='tv show library organizer',
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    entry_points={
        'console_scripts': ['librarizer=librarizer.librarizer:cli'],
    }
)
