from setuptools import setup, find_packages

setup(
    name="portfolio-optimization",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.3.0",
        "python-dotenv>=0.19.0",
        "yfinance>=0.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "bandit>=1.7.0",
        ],
    },
    author="Ali Yüksel",
    author_email="ali.yuksel@bahcesehir.edu.tr",
    description="Portföy optimizasyonu ve risk analizi için Python paketi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aliyksll/DOKTORA",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
) 