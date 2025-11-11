from setuptools import setup, find_packages

setup(
    name="ai_engg",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "rich>=13.0.0"
    ],
    python_requires=">=3.8",
)
