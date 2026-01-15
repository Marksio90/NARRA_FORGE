"""
Setup script for NARRA_FORGE
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="narra-forge",
    version="0.1.0",
    author="NARRA_FORGE Team",
    description="Autonomous Multi-World Narrative Generation System of Absolute Publishing Class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/NARRA_FORGE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.40.0",
        "openai>=1.50.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "narra-forge=narra_forge.__main__:main",
        ],
    },
)
