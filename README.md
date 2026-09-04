# Job Aggregator

A lightweight Python application that fetches remote tech jobs from the Himalayas RSS feed, stores them in a local SQLite database, and provides a command-line interface for browsing and keyword searching.

## Features

* Fetches remote jobs from the Himalayas RSS feed
* Parses RSS/XML job data
* Stores jobs in SQLite
* Prevents duplicate jobs
* Searches jobs by keyword across title, description, and company
* Handles fetch, parsing, and database errors gracefully
* Provides structured application logging
* Supports configuration through environment variables
* Includes automated tests, linting, formatting, and static type checking

## Tech Stack

* Python 3.12+
* SQLite
* requests
* pytest
* Ruff
* mypy

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Piptr67/job-aggregator.git
cd job-aggregator
```

### 2. Create and activate a virtual environment

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### View stored jobs

```bash
python main.py
```

This displays the latest jobs currently stored in the database.

### Fetch new jobs

```bash
python main.py --fetch
```

This fetches jobs from the Himalayas RSS feed and stores any new jobs in the database.

### Search jobs

```bash
python main.py --search <keyword>
```

For example:

```bash
python main.py --search python
```

The search checks the job title, description, and company name.

## Configuration

The application uses environment variables for runtime configuration. If they are not provided, the following defaults are used:

| Variable            | Default                          | Description                     |
| ------------------- | -------------------------------- | ------------------------------- |
| `DATABASE_PATH`     | `jobs.db`                        | Path to the SQLite database     |
| `HIMALAYAS_RSS_URL` | `https://himalayas.app/jobs/rss` | RSS feed URL                    |
| `FETCH_TIMEOUT`     | `10`                             | HTTP request timeout in seconds |
| `JOB_LIMIT`         | `50`                             | Maximum number of jobs returned |
| `LOG_LEVEL`         | `INFO`                           | Application logging level       |

For example:

```bash
export JOB_LIMIT=100
export FETCH_TIMEOUT=20
python main.py --fetch
```

On Windows PowerShell:

```powershell
$env:JOB_LIMIT="100"
$env:FETCH_TIMEOUT="20"
python main.py --fetch
```

## How It Works

The application follows a simple pipeline:

1. The Himalayas RSS feed is fetched using `requests`.
2. The RSS/XML response is parsed into `Job` objects.
3. Jobs are stored in SQLite using their unique link to prevent duplicates.
4. Stored jobs can be retrieved or searched through the CLI.
5. Application-level exceptions are used to handle fetch, parsing, and database failures without exposing low-level implementation details to the CLI.

## Project Structure

```text
job-aggregator/
├── tests/
│   ├── test_database.py
│   ├── test_himalayas_parser.py
│   ├── test_main.py
│   └── test_integration.py
├── conftest.py
├── config.py
├── database.py
├── exceptions.py
├── himalayas_parser.py
├── himalayas_source.py
├── job.py
├── logger.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Testing

Run the complete test suite with:

```bash
pytest -v
```

The test suite covers:

* RSS parsing
* Malformed feed handling
* Invalid job handling
* Database initialization and persistence
* Duplicate protection
* Job retrieval
* Keyword searching
* CLI behavior
* Integration between parsing and database persistence

The project currently contains **19 tests**.

## Code Quality

Run Ruff linting:

```bash
ruff check .
```

Format the project with:

```bash
ruff format .
```

Run static type checking with:

```bash
mypy .
```

All three checks are part of the project's development workflow.
