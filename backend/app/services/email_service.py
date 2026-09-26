import smtplib
import socket
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger("careerlens.email_service")

class EmailService:
    """
    Email abstraction service for CareerLens.
    Supports real SMTP delivery (STARTTLS / SSL) when configured via environment variables,
    and safe development-only logging and test inspection without leaking
    sensitive credentials or exposing tokens in production logs.
    """
    
    # In-memory storage for test verification and local development
    latest_dev_emails: List[Dict[str, Any]] = []

    @classmethod
    def is_configured(cls) -> bool:
        """
        Check if the SMTP service is configured with a host.
        """
        return bool(settings.SMTP_HOST and settings.SMTP_HOST.strip())

    @classmethod
    def send_password_reset_email(cls, to_email: str, reset_url: str) -> bool:
        subject = "Reset Your CareerLens Password"
        
        text_content = (
            f"Hello,\n\n"
            f"We received a request to reset the password for your CareerLens account.\n\n"
            f"Click the link below to set a new password:\n"
            f"{reset_url}\n\n"
            f"This link is valid for 30 minutes and can only be used once.\n"
            f"If you did not request this password reset, please ignore this email.\n\n"
            f"Regards,\n"
            f"The CareerLens Team"
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 24px; margin: 0;">
            <div style="max-width: 540px; margin: 0 auto; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; padding: 32px;">
                <h2 style="color: #6366f1; margin-top: 0;">CareerLens Password Reset</h2>
                <p style="font-size: 14px; line-height: 1.6; color: #cbd5e1;">
                    We received a request to reset the password for your CareerLens account (<strong>{to_email}</strong>).
                </p>
                <div style="margin: 28px 0; text-align: center;">
                    <a href="{reset_url}" style="background-color: #6366f1; color: #ffffff; padding: 12px 28px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 14px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="font-size: 12px; line-height: 1.6; color: #94a3b8;">
                    This link is single-use and will expire in <strong>30 minutes</strong>.<br/>
                    If you did not make this request, you can safely ignore this email.
                </p>
                <hr style="border: 0; border-top: 1px solid #334155; margin: 24px 0;" />
                <p style="font-size: 11px; color: #64748b;">
                    CareerLens © 2026 • AI-Powered Verified Career and Internship Matching Platform
                </p>
            </div>
        </body>
        </html>
        """

        # Record into development email inbox for testing & inspection
        record = {
            "to": to_email,
            "subject": subject,
            "reset_url": reset_url
        }
        cls.latest_dev_emails.append(record)
        # Keep only the last 20 emails
        if len(cls.latest_dev_emails) > 20:
            cls.latest_dev_emails.pop(0)

        # 1. Real SMTP dispatch if configured
        if cls.is_configured():
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.SMTP_FROM
                msg["To"] = to_email

                part1 = MIMEText(text_content, "plain")
                part2 = MIMEText(html_content, "html")
                msg.attach(part1)
                msg.attach(part2)

                # Connect via SSL (port 465) or STARTTLS (port 587/25)
                use_ssl = settings.SMTP_SSL or settings.SMTP_PORT == 465
                if use_ssl:
                    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                        if settings.SMTP_TLS:
                            server.starttls()
                        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                        server.send_message(msg)

                logger.info(f"[CareerLens Email Service] Successfully sent password reset email via SMTP to {to_email}")
                print(f"[CareerLens Email Service] Successfully dispatched password reset email via SMTP to {to_email}")
                return True

            except smtplib.SMTPAuthenticationError:
                logger.error("[CareerLens Email Service Error] SMTP Authentication failed. Verify SMTP_USERNAME and SMTP_PASSWORD.")
                print("[CareerLens Email Service Error] SMTP Authentication failed. Verify SMTP_USERNAME and SMTP_PASSWORD.")
                return False
            except (smtplib.SMTPException, socket.timeout, OSError) as e:
                logger.error(f"[CareerLens Email Service Error] Failed to send email via SMTP ({type(e).__name__}): {e}")
                print(f"[CareerLens Email Service Error] Failed to send email via SMTP ({type(e).__name__}): {e}")
                return False
            except Exception as e:
                logger.error(f"[CareerLens Email Service Error] Unexpected error sending email ({type(e).__name__}): {e}")
                print(f"[CareerLens Email Service Error] Unexpected error sending email ({type(e).__name__}): {e}")
                return False

        # 2. Unconfigured fallback
        is_production = settings.ENVIRONMENT.lower() == "production"
        if not is_production:
            logger.info(f"[CareerLens Dev Email] Password reset link for {to_email}: {reset_url}")
            print(f"[CareerLens Dev Email] Password reset link for {to_email}: {reset_url}")
            return True
        else:
            logger.warning("[CareerLens Email Service] SMTP is unconfigured (SMTP_HOST is empty). Real email cannot be dispatched.")
            print("[CareerLens Email Service] SMTP is unconfigured (SMTP_HOST is empty). Real email cannot be dispatched.")
            return False

