from setuptools import setup, find_packages

setup(
    name='auto-updater',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',  # For handling HTTP requests
        'tkinter',   # For GUI development (if using Python 3, tkinter is included by default)
    ],
    entry_points={
        'console_scripts': [
            'auto-updater=main:main',  # Assuming main.py has a main function to start the app
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple auto-updater application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/auto-updater',  # Replace with your project's URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)