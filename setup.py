from setuptools import setup, find_packages

setup(
    name="see",
    version="0.1.0",
    packages=find_packages(),
    scripts=['see'],
    author="Nishant Mohan",
    author_email="nishant040305@gmail.com",
    description="CLI Command Helper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nishant040305/see",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # List any dependencies here, e.g. 'pyperclip'
    ],
)
