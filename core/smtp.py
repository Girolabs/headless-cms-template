from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend
from core.models import EmailSettings


class EmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently, **kwargs):
        config = EmailSettings.load()

        super().__init__(
            fail_silently=fail_silently,
            host=config.email_host,
            port=config.email_port,
            username=config.email_user,
            password=config.email_password,
            use_tls=config.email_encryption == "TLS",
            use_ssl=config.email_encryption == "SSL",
        )
