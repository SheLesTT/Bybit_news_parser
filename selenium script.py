import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


options = webdriver.ChromeOptions()
options.add_argument('--headless')  #
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://announcements.bybit.com/en-US/?category=&page=1"

articles= []
driver.get(url)

for i in range(2,126):  # for some reason pages from 126 are not loading, on any browser i tried
    article_list = driver.find_element(By.CLASS_NAME, "article-list")
    links = article_list.find_elements(By.CLASS_NAME, "no-style")

    # need to check if the next page is loaded
    first_link = links[0]
    first_title = first_link.find_element(By.TAG_NAME, "span")

    for link in links:
        title = link.find_element(By.TAG_NAME, "span")
        articles.append([title.text, link.get_attribute("href")])

    article_list.find_element(By.CLASS_NAME, f"ant-pagination-item-{i}").click()
    with open("articles.csv", "a",encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(articles)
        articles = []

    # waiting until the next page is loaded
    while True:
        try:
            article_list_new = driver.find_element(By.CLASS_NAME, "article-list")
            links = article_list_new.find_elements(By.CLASS_NAME, "no-style")
            first_link_new = links[0]
            title = first_link_new.find_element(By.TAG_NAME, "span")
            if first_title != title:
                break
        except StaleElementReferenceException:
            pass
        except IndexError:
             pass
        finally:
            time.sleep(0.1)


def refresh_cur_articles_names():
    """function to refresh current articles names on a first page"""
    cur_names = []
    driver.get(url)

    article_list = driver.find_element(By.CLASS_NAME, "article-list")
    links = article_list.find_elements(By.CLASS_NAME, "no-style")

    for link in links:
        try:
            cur_names.append(link.find_element(By.TAG_NAME, "span").text)
        except StaleElementReferenceException:
            pass
    return cur_names

def append_article_to_csv(csv_file, title, link):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    print(title)
    with open(csv_file, "a",encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([title,link, formatted_datetime])


cur_articles_names = refresh_cur_articles_names()

# check if new article appeared on a main page
while True:
    driver.get(url)
    article_list = driver.find_element(By.CLASS_NAME, "article-list")
    links = article_list.find_elements(By.CLASS_NAME, "no-style")

    for link in links:
        try:
            title = link.find_element(By.TAG_NAME, "span").text

            if title not in cur_articles_names:
                append_article_to_csv("articles.csv", title, link.get_attribute("href"))
                cur_articles_names = refresh_cur_articles_names()
        except StaleElementReferenceException:
            pass

    time.sleep(1)
# time.sleep(10)


