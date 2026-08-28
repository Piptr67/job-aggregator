import argparse

from database import get_jobs, init_db, save_jobs, search_jobs
from himalayas_source import HimalayasSource

HIMALAYAS_RSS_URL = "https://himalayas.app/jobs/rss"

def main() -> None:
    parser = argparse.ArgumentParser(description="Job aggregator")
    parser.add_argument("--search", help="Search jobs by keyword")

    args = parser.parse_args()

    init_db()

    source = HimalayasSource(HIMALAYAS_RSS_URL)
    jobs = source.fetch()

    inserted = save_jobs(jobs)

    print(f"Fetched {len(jobs)} jobs")
    print(f"Inserted {inserted} new jobs")

    if args.search:
        saved_jobs = search_jobs(args.search)
        print(f"\nJobs matching '{args.search}':")
    else:
        saved_jobs = get_jobs()
        print("\nLatest jobs:")

    for job in saved_jobs:
        print(f"[{job.company}] {job.title}")
        print(job.link)
        print()

if __name__ == "__main__":
    main()