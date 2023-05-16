import random
import time
import requests
import re
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from colorama import Fore, Style
import emoji


def progress_bar(row_count, total_rows):
    percent = round((row_count / total_rows) * 100, 2)
    progress = int(100 * row_count / total_rows)
    bar = Fore.LIGHTGREEN_EX + "[" + "\u25AE" * progress + "_" * (100 - progress) + "]"
    print(f"{bar} {percent}%" + Style.RESET_ALL)


def count_total_lines(csv_file):
    with open(csv_file) as fp:
        total = 0
        for _ in fp:
            total += 1
    return total


def get_user_agent_list():
    user_agent_list = []
    with open('../scrapere/user-agents-unique.txt', 'r') as f:
        for line in f:
            user_agent_list.append(line.strip())
    return user_agent_list


def get_random_user_agent():
    user_agent_list = get_user_agent_list()
    return user_agent_list[0]


def generate_header():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Dnt': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_random_user_agent(),
        'X-Amzn-Trace-Id': 'Root=1-5ee7bae0-82260c065baf5ad7f0b3a3e3'
    }
    header = {'headers': headers}
    return header


def wait_random_time():
    time.sleep(random.randint(1, 3))


def is_valid_email(email):
    if email.endswith('.png') or email.endswith('.jpg') or email.endswith('.gif') or email.endswith('.svg'):
        return False
    if email.endswith('@sentry-next.wixpress.com') or email.endswith('@sentry.io') or email.endswith('@sentry.wixpress.com') or email.endswith('@example.com') or email.endswith('@prestashop.com') or email.endswith('@202-ecommerce.com') or email.endswith('@e-mail.com'):
        return False
    match = re.match(r'^[a-zA-Z]+[.][a-zA-Z]+@', email)
    if match and match.group() == 'nombre.apellido@':
        return False
    return True


def filter_valid_emails_from_file(file_name):
    valid_emails = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if is_valid_email(row[1]):
                valid_emails.append(row)
    print("Found " + str(len(valid_emails)) + " valid emails")
    with open('valid_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        for row in valid_emails:
            writer = csv.DictWriter(f, fieldnames=['url', 'email'])
            writer.writerow({'url': row[0], 'email': row[1]})
    print("Wrote CSV file with " + str(len(valid_emails)) + " valid emails")


def scrap_phones(url):
    phones = []
    counter = 0
    try:
        counter += 1
        print(f"Crawling through {url}...")
        response = requests.get(url, generate_header())
        soup = BeautifulSoup(response.content, 'html.parser')
        for phone in re.findall(r'(?:\+34|0034)?\s?(?:6|9)(?:\d\s?\d{2}\s?\d{2}\s?\d{2}|\d{2}\s?\d{3}\s?\d{3}|\d{3}\s?\d{2}\s?\d{2})', str(soup)):
            phone = phone.replace(" ", "")
            phone = phone.replace("+34", "")
            phone = phone.replace("0034", "")
            if len(phone) == 9:
                phones.add(phone)
                with open('phones.csv', 'a', newline='') as csvfile:
                    fieldnames = ['url', 'phone']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'url': url, 'phone': phone})
                print(f"Found phone: {phone}, added to phones.csv")
    except requests.exceptions.RequestException as e:
        print(f"Failed to crawl {url}: {e}")
    print(Fore.LIGHTGREEN_EX + "Found " + str(len(phones)) + " phone numbers in " + url)


def scrap_emails(url):
    emails = []
    counter = 0
    try:
        counter += 1
        print(f"Crawling through {url}...")
        response = requests.get(url, generate_header())
        soup = BeautifulSoup(response.content, 'html.parser')
        for email in re.findall(r'[\w\.-]+@[\w\.-]+', str(soup)):
            if is_valid_email(email):
                emails.append(email)
                with open('emails.csv', 'a', newline='') as csvfile:
                    fieldnames = ['url', 'email']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'url': url, 'email': email})
                print(f"Found email: {email}, added to emails.csv")
    except requests.exceptions.RequestException as e:
        print(f"Failed to crawl {url}: {e}")
    print(Fore.LIGHTGREEN_EX + "Found " + str(len(emails)) + " emails in " + url)

