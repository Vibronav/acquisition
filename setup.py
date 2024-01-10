from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='vnav-acquisition',
    version='1.1.0',
    description='Vibronav acquisition interface',
    author='Dominik Rzepka',
    author_email='dominik.rzepka@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={},
    package_data={
        'vnav_acquisition': ['*.js', '*.css', '*.json']
    },
    data_files=[],
    entry_points={
        'console_scripts': ['vnav_acquisition=vnav_acquisition.webserver:main'],
    }
)
