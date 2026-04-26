from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="neural-agent",
    version="1.0.0",
    author="Neural Agent Team",
    author_email="agent@neural.dev",
    description="An advanced AI agent with memory, web access, task execution, and kill switch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robeast430-create/Testing-grounds",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "sentence-transformers>=2.2.0",
        "chromadb>=0.4.0",
        "watchdog>=3.0.0",
        "pytz>=2023.3",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neural-agent=neural_agent.cli:main",
            "neural-agent-web=neural_agent.cli:web",
        ],
    },
    package_data={
        "neural_agent": ["web/*.html"],
    },
    include_package_data=True,
)