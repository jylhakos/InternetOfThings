#!/usr/bin/env python3
"""Setup script for Feature Learning project."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="feature-learning-pytorch",
    version="1.0.0",
    author="Feature Learning Team",
    author_email="team@example.com",
    description="Feature Learning with PyTorch: CNNs, RNNs, Autoencoders, and Transfer Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/feature-learning-pytorch",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.10.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "gpu": [
            "torch",
            "torchvision", 
            "torchaudio",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "notebook>=6.5.0",
            "jupyterlab>=3.4.0",
            "ipywidgets>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "train-cnn=training.train_cnn:main",
            "train-rnn=training.train_rnn:main", 
            "train-autoencoder=training.train_autoencoder:main",
            "train-transfer=training.train_transfer_learning:main",
            "extract-features=utils.feature_extraction:main",
            "evaluate-features=evaluation.evaluate_features:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/feature-learning-pytorch/issues",
        "Source": "https://github.com/your-username/feature-learning-pytorch",
        "Documentation": "https://feature-learning-pytorch.readthedocs.io/",
    },
)
