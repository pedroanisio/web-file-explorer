"""
Setup script for Flask File Explorer package.
"""
from setuptools import setup, find_packages

# Read version from the package
with open('src/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        version = '0.0.0'

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='flask-file-explorer',
    version=version,
    description='A web-based file explorer built with Flask',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/flask-file-explorer',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=[
        'flask>=2.0.0',
        'python-dotenv>=0.20.0',
        'werkzeug>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-flask>=1.2.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.950',
        ],
    },
    entry_points={
        'console_scripts': [
            'flask-file-explorer=flask_file_explorer:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: System :: Filesystems',
    ],
)