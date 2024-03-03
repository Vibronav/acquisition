from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='vnav-acquisition',
    version='1.5.1',
    description='Vibronav acquisition tools',
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
        'vnav_acquisition': ['*.js', '*.css', '*.html', '*.txt']
    },
    data_files=[],
    entry_points={
        'console_scripts': ['vnav_acquisition=vnav_acquisition.webserver:main',
                            'vnav_wav_process=vnav_acquisition.clean:main',
                            'vnav_audio_video_sync=vnav_acquisition.sync:main'],
    }
)
