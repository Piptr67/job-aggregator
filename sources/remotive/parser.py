from exceptions import ParserError
from job import Job


class RemotiveParser:
    def parse(self, data: dict) -> list[Job]:
        try:
            jobs_data = data["jobs"]
        except KeyError as e:
            raise ParserError("Missing jobs data") from e
        
        jobs = []
        for job_data in jobs_data:
            jobs.append(self._data_to_job(job_data))

        return jobs

    def _data_to_job(self, data: dict) -> Job:
        try:
            return Job(
                title=data["title"],
                description=data["description"],
                link=data["url"],
                pub_date=data["publication_date"],
                company=data["company_name"],
            )
        except KeyError as e:
            raise ParserError("Missing required job field") from e