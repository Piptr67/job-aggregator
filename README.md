# Job Aggregator

A lightweight Python application that fetches remote jobs from the Himalayas RSS feed, stores them in a local SQLite database, and provides a CLI for browsing and keyword searching.

## Features

* Fetches jobs from the Himalayas RSS feed
* Parses RSS/XML job data
* Stores jobs in SQLite
* Prevents duplicate jobs
* Searches jobs by keyword across title, description, and company
* Provides a simple command-line interface

## Tech Stack

* Python 3.12+
* SQLite
* requests
* pytest

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd job-aggregator
```

### 2. Create and activate a virtual environment

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Fetch and display the latest jobs:

```bash
python main.py
```

Search jobs by keyword:

```bash
python main.py --search <keyword>
```

The search checks the job title, description, and company name.

## Project Structure

```text
job-aggregator/
├── tests/
│   ├── test_database.py
│   └── test_himalayas_parser.py
├── conftest.py
├── database.py
├── himalayas_parser.py
├── himalayas_source.py
├── job.py
├── main.py
├── requirements.txt
└── .gitignore
```

## Testing

Run the test suite with:

```bash
pytest -v
```

The test suite covers RSS parsing, error handling, database persistence, duplicate protection, job retrieval, and keyword searching.