import resend

from job_aggregator.core.config import settings

resend.api_key = settings.resend_api_key


def send_verification_email(email: str, token: str) -> None:
    verification_link = (
        f"{settings.base_url.rstrip('/')}/api/v1/auth/verify-email?token={token}"
    )

    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [email],
            "subject": "Verify your email address",
            "html": f"""
                <h2>Welcome!</h2>
                <p>Click the link below to verify your email address:</p>
                <a href="{verification_link}">Verify email</a>
                <p>If you didn't create an account, you can ignore this email.</p>
            """,
        }
    )
