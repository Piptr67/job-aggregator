from job import Job

def search_keyword(jobs: list[Job], keyword: str) -> list[Job]:
    kw = keyword.lower()
    return [job for job in jobs
            if kw in job.title.lower()
            or kw in job.description.lower()
            or kw in job.company.lower()
            ]
def filter_by_company(jobs: list[Job], company: str) -> list[Job]:
    cmp = company.lower()
    return [job for job in jobs if cmp in job.company.lower()]

if __name__ == "__main__":
    from himalayas_source import HimalayasSource

    source = HimalayasSource("https://himalayas.app/jobs/rss")
    jobs = source.fetch()

    keyword_jobs = search_keyword(jobs, "remote")
    company_jobs = filter_by_company(jobs, "micro1")

    print(f"Python jobs: {len(keyword_jobs)}")
    print(keyword_jobs[:2])

    print(f"micro1 jobs: {len(company_jobs)}")
    print(company_jobs[:2])