from setuptools import setup, find_packages

__version__ = '0.1.1'

setup(
    name='seafileapi',
    version=__version__,
    license='BSD',
    description='Python client for Seafile Web API',
    author='seafile',
    author_email='support@seafile.com',
    url='https://github.com/haiwen/python-seafile',
    platforms='any',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # und so weiter, je nachdem was Ihr unterstützt
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    # Falls ihr Python <3 nicht mehr unterstützen wollt,
    # könnt ihr das hier explizit festlegen:
    python_requires='>=3.6',
)

