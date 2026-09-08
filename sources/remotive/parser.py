from job import Job


class RemotiveParser:
    def parse(self, data: dict) -> list[Job]:
        jobs = []
        for job_data in data["jobs"]:
            jobs.append(self._data_to_job(job_data))

        return jobs

    def _data_to_job(self, data: dict) -> Job:
        return Job(
            title=data["title"],
            description=data["description"],
            link=data["url"],
            pub_date=data["publication_date"],
            company=data["company_name"],
        )