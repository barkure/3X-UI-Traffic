import requests
from requests.packages import urllib3
from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Config
# 3X-UI Config
base_url = ''
username = ''
password = ''
# Email Config
smtp_server = 'smtp.office365.com'
smtp_port = 587
email_address = ''
email_password = ''
to_address = ['abc@xxx.com', 'wsgwy@jack.com']

# Disable SSL warnings
urllib3.disable_warnings()

# Login and get cookie
login_url = f'{base_url}/login?username={username}&password={password}'
login_response = requests.post(login_url, verify=False)
print(login_response.text)
cookie = login_response.cookies.get_dict()

# Get list of inbounds
url = f'{base_url}/panel/api/inbounds/list'
headers = {
    'Cookie': 'session=' + cookie['session']
}
response = requests.get(url, verify=False, headers=headers)

# Parse the response, get traffics data and calculate the amount
unit_cost = 0.65 # CNY/GiB
data = response.json()
obj = data['obj']
client_traffics = []
for i in obj:
    new_traffic = {
        'id': i['id'],
        'remark': i['remark'],
        'up(MiB)': round(i['up'] / (1024**2), 2),
        'down(MiB)': round(i['down'] / (1024**2), 2),
        'total(GiB)': round((i['up'] + i['down']) / (1024**3), 2),
        'amount(CNY)': round((i['up'] + i['down']) / (1024**3) * unit_cost, 2)
    }
    client_traffics.append(new_traffic)


# Print the traffics data in a table
table = PrettyTable()
table.field_names = ["id", "remark", "up(MiB)", "down(MiB)", "total(GiB)", "amount(CNY)"]

for traffic in client_traffics:
    table.add_row([traffic['id'], traffic['remark'], traffic['up(MiB)'], traffic['down(MiB)'], traffic['total(GiB)'], traffic['amount(CNY)']])

table_str = table.get_string()
print(table_str)


# Table 2 image
image = Image.new('RGB', (1080, 600), color = (0, 0, 0))
# add info to text
now = datetime.now()
time_str = now.strftime("%m/%d/%Y %H:%M:%S")
text = f'{table_str}\n\nStatistics at {time_str}.'

d = ImageDraw.Draw(image)
# loading equal width font
font = ImageFont.truetype("fonts/Ubuntu Mono derivative Powerline.ttf", 30)
d.text((20,20), text, fill=(255,255,255), font=font)
image.save('text.png')


# Send the image to Email
msg = MIMEMultipart()
msg['Subject'] = 'Traffic Statistics'
msg['From'] = email_address
msg['To'] = ', '.join(to_address)

# Attach the image
with open('text.png', 'rb') as f:
    image = MIMEImage(f.read())
    msg.attach(image)

# Send the email
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(email_address, email_password)
server.send_message(msg)
server.quit()
print('Email sent successfully')

