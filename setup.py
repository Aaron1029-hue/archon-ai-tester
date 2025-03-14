from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="archon-agent-tester",
    version="0.1.0",
    author="AI Developer",
    author_email="developer@example.com",
    description="An AI agent testing system built for Archon using OpenRouter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aaron1029-hue/archon-ai-tester",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.3.0", 
            "pytest>=7.3.1",
            "pytest-asyncio>=0.21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "archon-tester=archon_agent_tester.cli:main",
        ],
    },
)