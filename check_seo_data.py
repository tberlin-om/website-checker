import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

df = pd.read_csv('static_seo_data.csv')

sender = os.getenv('SMTP_USERNAME')
password = os.getenv('SMTP_PASSWORD')
receivers = ["RECEIVER_EMAIL"]

smtp_server = "YOUR_SMTP_SERVER"
smtp_port = 25

all_changes = []

for index, row in df.iterrows():
    url = row['url']
    response = requests.get(url)
    changes = []

    if response.status_code != row['statuscode']:
        changes.append(f"The statuscode for {url} has changed. Old value: {row['statuscode']}, New value: {response.status_code}.")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find('title')
    if title and pd.notnull(row['title']) and title.text.strip() != row['title'].strip():
        changes.append(f"The title for {url} has changed. Old value: {row['title']}, New value: {title.text.strip()}.")

    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description and pd.notnull(row['meta-description']) and meta_description['content'].strip() != row['meta-description'].strip():
        changes.append(f"The meta-description for {url} has changed. Old value: {row['meta-description']}, New value: {meta_description['content'].strip()}.")

    h1 = soup.find('h1')
    if h1 and pd.notnull(row['h1']) and h1.text.strip() != row['h1'].strip():
        changes.append(f"The h1 for {url} has changed. Old value: {row['h1']}, New value: {h1.text.strip()}.")

    meta_robots = soup.find('meta', attrs={'name': 'robots'})
    if meta_robots and pd.notnull(row['meta-robots']) and meta_robots['content'].strip() != row['meta-robots'].strip():
        changes.append(f"The meta-robots for {url} has changed. Old value: {row['meta-robots']}, New value: {meta_robots['content'].strip()}.")

    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical and pd.notnull(row['canonical']) and canonical['href'].strip() != row['canonical'].strip():
        changes.append(f"The canonical for {url} has changed. Old value: {row['canonical']}, New value: {canonical['href'].strip()}.")

    all_changes.extend(changes)

if all_changes:
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(receivers)
    msg['Subject'] = "Website Monitoring Alert"
    body = "\n".join(all_changes)
    msg.attach(MIMEText(body, 'plain'))
        
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, receivers, text)
    server.quit()
