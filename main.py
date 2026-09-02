import argparse

from database import get_jobs, init_db, save_jobs, search_jobs
from himalayas_source import HimalayasSource

HIMALAYAS_RSS_URL = "https://himalayas.app/jobs/rss"

def main() -> None:
    parser = argparse.ArgumentParser(description="Job aggregator")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--search", help="Search jobs by keyword")
    group.add_argument("--fetch", action="store_true", help="Fetch new jobs")

    args = parser.parse_args()

    init_db()

    if args.fetch:
        source = HimalayasSource(HIMALAYAS_RSS_URL)
        jobs = source.fetch()
        inserted = save_jobs(jobs)

        print(f"Fetched {len(jobs)} jobs")
        print(f"Inserted {inserted} new jobs")
        return

    if args.search:
        saved_jobs = search_jobs(args.search)
        print(f"\nJobs matching '{args.search}':")
    else:
        saved_jobs = get_jobs() 
        print("\nLatest jobs:")

    if not saved_jobs:
        print("No jobs found.")
        return
    
    for job in saved_jobs:
        print(f"[{job.company}] {job.title}")
        print(job.link)
        print()


if __name__ == "__main__":
    main()