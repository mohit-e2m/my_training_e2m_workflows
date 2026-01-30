"""
Email Utility for Smart Chatbot
Handles sending support ticket notifications via SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailSender:
    """Handles email sending functionality"""
    
    def __init__(self, smtp_settings):
        """
        Initialize email sender with SMTP settings
        
        Args:
            smtp_settings: SMTPSettings object from database
        """
        self.sender_email = smtp_settings.sender_email
        self.smtp_server = smtp_settings.smtp_server
        self.smtp_port = smtp_settings.smtp_port
        self.smtp_username = smtp_settings.smtp_username
        self.smtp_password = smtp_settings.smtp_password
        self.use_ssl = bool(smtp_settings.use_ssl)
        self.recipient_email = smtp_settings.recipient_email
    
    def send_support_ticket_email(self, user_name, user_email, subject, message, ticket_id):
        """
        Send support ticket notification email
        
        Args:
            user_name (str): Name of the user who created the ticket
            user_email (str): Email of the user
            subject (str): Ticket subject
            message (str): Ticket message
            ticket_id (int): Ticket ID
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f'New Support Ticket #{ticket_id}: {subject}'
            
            # Create HTML email body
            html_body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 8px 8px 0 0;
                        }}
                        .content {{
                            background: #f9fafb;
                            padding: 30px;
                            border: 1px solid #e5e7eb;
                        }}
                        .info-row {{
                            margin: 15px 0;
                            padding: 10px;
                            background: white;
                            border-left: 4px solid #00d4ff;
                        }}
                        .label {{
                            font-weight: bold;
                            color: #6b7280;
                            font-size: 0.875rem;
                        }}
                        .value {{
                            color: #1f2937;
                            margin-top: 5px;
                        }}
                        .message-box {{
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            margin-top: 20px;
                            border: 1px solid #e5e7eb;
                        }}
                        .footer {{
                            text-align: center;
                            padding: 20px;
                            color: #6b7280;
                            font-size: 0.875rem;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2 style="margin: 0;">🎫 New Support Ticket</h2>
                            <p style="margin: 5px 0 0 0; opacity: 0.9;">Ticket #{ticket_id}</p>
                        </div>
                        
                        <div class="content">
                            <div class="info-row">
                                <div class="label">FROM</div>
                                <div class="value">{user_name}</div>
                            </div>
                            
                            <div class="info-row">
                                <div class="label">EMAIL</div>
                                <div class="value"><a href="mailto:{user_email}">{user_email}</a></div>
                            </div>
                            
                            <div class="info-row">
                                <div class="label">SUBJECT</div>
                                <div class="value">{subject}</div>
                            </div>
                            
                            <div class="info-row">
                                <div class="label">DATE</div>
                                <div class="value">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
                            </div>
                            
                            <div class="message-box">
                                <div class="label">MESSAGE</div>
                                <div class="value" style="margin-top: 10px; white-space: pre-wrap;">{message}</div>
                            </div>
                        </div>
                        
                        <div class="footer">
                            <p>This is an automated notification from E2M Solutions Smart Chatbot</p>
                            <p>Please respond to the user at <a href="mailto:{user_email}">{user_email}</a></p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
New Support Ticket #{ticket_id}

From: {user_name}
Email: {user_email}
Subject: {subject}
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Message:
{message}

---
This is an automated notification from E2M Solutions Smart Chatbot
Please respond to the user at {user_email}
            """
            
            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            if self.use_ssl:
                # Use SSL
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # Use STARTTLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            
            print(f"Support ticket email sent successfully for ticket #{ticket_id}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
