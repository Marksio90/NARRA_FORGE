"""
NARRA_FORGE - Batch Production Engine for Publishing-Grade Narratives
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="narra-forge",
    version="2.0.0",
    author="NARRA_FORGE Team",
    description="Batch production engine for publishing-grade narratives (OpenAI-powered)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Marksio90/NARRA_FORGE",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.54.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "sqlalchemy>=2.0.35",
        "aiosqlite>=0.20.0",
        "python-dotenv>=1.0.0",
        "tenacity>=9.0.0",
        "tiktoken>=0.8.0",
        "click>=8.1.0",
        "rich>=13.9.0",
        "tqdm>=4.67.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-asyncio>=0.24.0",
            "pytest-cov>=6.0.0",
            "black>=24.10.0",
            "isort>=5.13.0",
            "ruff>=0.7.0",
            "mypy>=1.13.0",
        ],
        "monitoring": [
            "prometheus-client>=0.20.0",
            "structlog>=24.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "narra-forge=narra_forge.cli:main",
        ],
    },
)
