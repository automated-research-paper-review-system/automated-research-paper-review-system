from selenium import webdriver
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import os


# Check your chrome version and download appropriate executable from https://chromedriver.chromium.org/downloads
# update executable_path argument to the location of chromedriver.exe
def configure_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path='C:/Users/KarnaveeKamdar/Downloads/chromedriver_win32/chromedriver.exe',
                              options=chrome_options)
    # driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrome_options)
    driver.implicitly_wait(10)
    return driver


def get_title(soup):
    row = dict()
    try:
        row['title'] = [soup.find('h4').text.strip()]
    except Exception as e:
        print(e)
        row['title'] = [None]
    finally:
        return row


def get_authors(soup):
    row = dict()
    try:
        row['authors'] = [soup.find_all('i')[-1].text.strip()]
    except Exception as e:
        print(e)
        row['authors'] = [None]
    finally:
        return row


def get_abstract(soup):
    row = dict()
    try:
        row['abstract'] = [soup.find_all('p')[-1].text.strip()]
    except Exception as e:
        print(e)
        row['abstract'] = [None]
    finally:
        return row


def download_pdf(base_url, pdf_dir):
    row = dict()
    try:
        filename = pdf_dir + base_url.split('/')[-1]
        response = requests.get(base_url, stream=True)

        with open(filename, 'wb') as pdf:
            for chunk in response.iter_content(chunk_size=1000000):
                if chunk:
                    pdf.write(chunk)
        row['downloaded_pdf'] = [True]
    except Exception as e:
        print(e)
        row['downloaded_pdf'] = [False]
    finally:
        return row


def get_reviews(base_url):
    row = dict()
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        reviewers = soup.find_all('h3')
        # print(reviewers)
        reviews = soup.find_all('div')
        # print(reviews)
        r = dict()
        for reviewer, review in zip(reviewers, reviews):
            r[reviewer.text.strip()] = review.text.strip()
        row['reviews'] = [r]
    except Exception as e:
        print(e)
        row['reviews'] = [None]
    finally:
        return row


def get_meta_review(base_url):
    row = dict()
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_review = [soup.find('div').text.strip()]
        row['meta_review'] = meta_review
    except Exception as e:
        print(e)
        row['meta_review'] = [None]
    finally:
        return row


if __name__ == '__main__':
    driver = configure_webdriver()
    parent_url = 'https://proceedings.neurips.cc/paper/2019'
    year = parent_url.split('/')[-1]

    pdf_dir = f'./raw-data/{year}/'
    processed_dir = f'./processed-data/{year}/'

    if not os.path.isdir(pdf_dir):
        os.makedirs(pdf_dir)

    if not os.path.isdir(processed_dir):
        os.makedirs(processed_dir)

    driver.get(parent_url)

    # all the papers html links in WebElement format
    html_links = driver.find_elements_by_xpath('/html/body/div[2]/div/ul/li')

    dataframe = pd.DataFrame()

    for index in range(len(html_links)):
        row = dict()
        base_url = html_links[index].find_element_by_tag_name('a').get_attribute('href')

        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        row['base_url'] = [base_url]

        row.update(get_title(soup))

        row.update(get_authors(soup))

        row.update(get_abstract(soup))

        base_url = base_url.replace('hash', 'file')

        # pdf_link
        pdf_link = base_url.replace('Abstract.html', 'Paper.pdf')
        row['pdf_link'] = [pdf_link]
        row.update(download_pdf(pdf_link, pdf_dir))

        # reviews_link
        reviews_link = base_url.replace('Abstract.html', 'Reviews.html')
        row['reviews_link'] = [reviews_link]
        row.update(get_reviews(reviews_link))

        # meta_review_link
        row['meta_review_link'] = base_url.replace('Abstract.html', 'MetaReview.html')
        meta_review_link = row['meta_review_link']
        row.update(get_meta_review(meta_review_link))

        df = pd.DataFrame(row)
        dataframe = dataframe.append(df)
        time.sleep(random.randint(1, 5))

    print(dataframe.shape)
    dataframe.to_csv('data.csv')

    os.system(f'java -Xmx6g -jar science-parse-cli-assembly-2.0.3.jar {pdf_dir} -o {processed_dir}')
