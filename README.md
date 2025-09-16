# Ethical AI in ML Competitions

This project aims to analyze the prevalence of ethical AI considerations in AI and ML competitions hosted on platforms like Kaggle.

## Project Goal

The primary goal is to scrape data from competition websites and analyze whether topics like fairness, bias, data privacy, and transparency are mentioned.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/makam2901/ethicalAI.git
    cd ethicalAI
    ```

2.  **Create and activate the Conda environment:**
    ```bash
    conda create --name ethical-ai python=3.10 -y
    conda activate ethical-ai
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

To start the scraping process, run the main script:
```bash
python src/main.py
