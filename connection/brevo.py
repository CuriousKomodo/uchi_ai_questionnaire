# pip install brevo-python python-dotenv

import os
from typing import Optional

from dotenv import load_dotenv
from brevo_python import Configuration, ApiClient, SendSmtpEmail
from brevo_python.api.transactional_emails_api import TransactionalEmailsApi
from brevo_python.rest import ApiException


class Brevo:
    """
    Minimal Brevo wrapper with a single method:
      send_welcome_email(recipient_email, first_name)

    Env vars:
      - BREVO_API_KEY (required)
      - BREVO_WELCOME_TEMPLATE_ID (optional if you pass template_id in __init__)
    """

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("BREVO_API_KEY")

        cfg = Configuration()
        cfg.host = "https://api.brevo.com/v3"
        cfg.api_key["api-key"] = api_key
        self._cfg = cfg  # reuse this config on every call
        self.welcome_template_id = 2

    def send_welcome_email(self, recipient_email: str, first_name: str):
        """
        Sends the Welcome template to the given recipient.
        Returns the Brevo API response object on success, or raises ApiException on failure.
        """
        payload = SendSmtpEmail(
            to=[{"email": recipient_email, "name": first_name}],
            template_id=self.welcome_template_id,
            params={"firstName": first_name},
        )

        try:
            with ApiClient(self._cfg) as client:
                api = TransactionalEmailsApi(client)
                return api.send_transac_email(payload)
        except ApiException as e:
            raise e


if __name__ == "__main__":
    brevo = Brevo(template_id=2)  # or rely on BREVO_WELCOME_TEMPLATE_ID
    resp = brevo.send_welcome_email("hu.kefei@yahoo.co.uk", "Kefei")
    print("✅ Sent:", resp)
