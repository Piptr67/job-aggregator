import argparse

from database import get_jobs, init_db, save_jobs, search_jobs
from himalayas_source import HimalayasSource
from config import Settings
from logger import setup_logger
from exceptions import DatabaseError, FetchError, ParserError


def main() -> None:
    parser = argparse.ArgumentParser(description="Job aggregator")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--search", help="Search jobs by keyword")
    group.add_argument("--fetch", action="store_true", help="Fetch new jobs")

    args = parser.parse_args()

    settings = Settings.from_env()
    logger = setup_logger(settings.log_level)

    try:
        init_db(settings.database_path)

        if args.fetch:
            source = HimalayasSource(
                settings.himalayas_rss_url, 
                settings.fetch_timeout,
            )
            jobs = source.fetch()
            inserted = save_jobs(jobs, settings.database_path)

            logger.info("Fetched %d jobs", len(jobs))
            logger.info("Inserted %d new jobs", inserted)
            return

        if args.search:
            saved_jobs = search_jobs(
                args.search, settings.job_limit,
                settings.database_path,
            )
            print(f"\nJobs matching '{args.search}':")
        else:
            saved_jobs = get_jobs(settings.job_limit, settings.database_path) 
            print("\nLatest jobs:")

        if not saved_jobs:
            print("No jobs found.")
            return
        
        for job in saved_jobs:
            print(f"[{job.company}] {job.title}")
            print(job.link)
            print()
    except (FetchError, ParserError, DatabaseError) as e:
        logger.error("%s", e)
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()