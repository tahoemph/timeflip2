# Timeflip2 Data Transformer

A Python tool for transforming Timeflip2 CSV exports into a week-based task summary format.

## Features
- Parses Timeflip2 CSV exports
- Aggregates task hours by week
- Generates a task-by-week summary matrix
- Handles semicolon-delimited CSV files

## Setup

### Prerequisites
- Python 3.13+
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/timeflip2.git
cd timeflip2
```

2. Create and activate virtual environment:

On Unix/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your Timeflip2 CSV export in the `data` directory
2. Run the transformer:
```bash
python src/main.py
```

The transformed output will be saved as `data/transformed_output.csv`

## Development

### Running Tests

Make sure you're in the virtual environment, then run:
```bash
pytest src/test_timeflip_transformer.py -v
```

### Project Structure
```
.
├── .venv/                 # Virtual environment (created after setup)
├── data/                  # Data directory
│   └── example.csv       # Input Timeflip2 data
├── src/                  # Source code
│   ├── __init__.py
│   ├── main.py
│   ├── timeflip_transformer.py
│   └── test_timeflip_transformer.py
├── README.md
└── requirements.txt
```

## Input Format

The tool expects Timeflip2 CSV exports with the following structure:
- Semicolon-delimited CSV
- Weekly sections starting with "Week #"
- Task rows containing task name and hours
- Daily breakdowns by task

Example input structure:
```csv
Account:;User Name;;;;;;;
From:;01.01.2025;;To:;11.01.2025;;;;
Week #1;;;;29.12.2024;30.12.2024;31.12.2024;...
Tag;Task;Time;Hour Rate;Sun;Mon;Tue;...
-;Code;7.75;;;;;...
;Slack;6.39;;;;;...
```

## Output Format

The tool generates a CSV with:
- Tasks as rows
- Weeks as columns
- Total hours per task per week

Example output:
```csv
Task,Week 1,Week 2
Code,7.75,5.89
Slack,6.39,15.45
```
