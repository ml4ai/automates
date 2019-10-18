from setuptools import setup

setup(
    name="pdfalign",
    description="A tool for annotating and aligning equations and text in scientific papers",
    url="https://github.com/ml4ai/automates",
    author="ML4AI",
    version="0.0.1",
    install_requires=[
        "tqdm",
        "lxml",
        "webcolors",
        "pdf2image",
        "pillow",
        "pdfminer.six"
    ],
    python_requires=">=3.0",
    entry_points={
        "console_scripts": [
            "pdfalign = pdfalign:main",
        ]
    },
)
