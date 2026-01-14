from setuptools import find_packages, setup

setup(
    name="whisper-api-wrapper",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "openai>=1.12.0",
        "pydub>=0.25.1",
        "click>=8.1.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.3",
    ],
    entry_points={
        "console_scripts": ["whisper-cli=whisper_cli.cli:main"],
    },
    python_requires=">=3.9",
)
