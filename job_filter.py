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