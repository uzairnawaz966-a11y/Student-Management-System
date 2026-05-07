import time
import logging
from django.core.mail import send_mail
from django.conf import settings


class EmailClient:

    logger = logging.getLogger(__name__)

    def retry_mechanism(self, func, retries, delay, *args, **kwargs):
        """
        Generic retry mechanis which accepts:
        1.   Function to call
        2.   Number of attempts
        3.   Seconds to wait between attempts
        4.   Arguments and Keyword arguments to pass into function
        """

        for attempt in range(1, retries + 1):
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"Call succeeded on attempt {attempt} for function {func.__name__}")
                return result
            except Exception as e:
                self.logger.error(f"Attempt {attempt} Failed for function {func.__name__}, Exception cause: {str(e)}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    self.logger.error(f"Request Failed for function {func.__name__} after {attempt} tries")
                    raise Exception(f"Failed to send activation link after {retries} attempts, Exception cause: {str(e)}")


    def send_verification_email(self, user_email, activation_link):
        subject = "Verify Your Email Address"
        message = f"""
                Dear User,

                Thank you for registering with Student Management System. Your Inactive account has been created.

                To complete your account setup, please verify your email address by clicking the link below:

                {activation_link}

                This verification link will expire soon for security reasons.

                If you did not create this account, someone is using your email address to login to some sites. Your email address will not be used without verification.

                For any assistance, Feel free to contact our support team.                

                Best regards,  
                Student Management System Team
            """

        def send_email_to_users():
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False
            )
            return True

        result = self.retry_mechanism(send_email_to_users, retries=3, delay=5)
        return result