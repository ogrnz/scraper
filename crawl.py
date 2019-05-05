import urllib.request
import re
import string
from datetime import datetime
from bs4 import BeautifulSoup
import mysql.connector
import sys
import logging

logging.basicConfig(filename = 'crawls.log', format = '%(asctime)s:%(levelname)s: %(message)s', level = logging.DEBUG)

urls = ["https://www.lemonde.fr/", 
        "http://www.lefigaro.fr/",
        "https://www.liberation.fr/", 
        "https://www.humanite.fr/", 
        "https://www.lesechos.fr/"]
        
        
JOURNAL_IDS = {
    "Le Monde": 1,
    "Le Figaro": 2,
    "Liberation": 3,
    "L Humanite": 4,
    "Les Echos": 5
}

try:
    connection = mysql.connector.connect(host='localhost',
                                        user='root',
                                        password='',
                                        db='scraper')
except Exception as e:
    logging.error(f"Error connecting to db: {e}")
    sys.exit('Execution failed')


def cleanList(toclean):
    translator = str.maketrans(dict.fromkeys(string.punctuation))
    cleaned = []
    characters = [u'\\xa0', u'\xa0', u'\u2009',
                  u'«', u'»', u"’", u"-", u":", u'"']
    for item in toclean:
        for character in characters:
            item = str(item).replace(character, u' ')
        cleaned.append(item.translate(translator).lower())
    return cleaned


def get_articles_titles_LM():

    page_content = urllib.request.urlopen(urls[0])
    soup = BeautifulSoup(page_content, 'html.parser')

    soup_articles_titles = soup.find_all(class_='article__title')
    regex_span = re.compile('<span|<a')
    soup_titles_parts = []

    for title in soup_articles_titles:

        for i, title_part in enumerate(title.contents):
            if regex_span.search(str(title_part)):
                title.contents.pop(i)

        for title_part in enumerate(title.contents):
            if title_part == ' ':
                title.contents.pop(i)

        soup_titles_parts.append(title.contents)

    final_cleaned_list = cleanList(soup_titles_parts)
    final_original_list = soup_titles_parts
    return final_cleaned_list, final_original_list


def get_articles_titles_LF():

    page_content = urllib.request.urlopen(urls[1])
    soup = BeautifulSoup(page_content, 'html.parser')

    soup_articles_titles = soup.find_all(class_="fig-profile__headline")
    soup_titles_parts = []
    for part in soup_articles_titles:
        soup_titles_parts.append(part.get_text(strip=True))

    final_cleaned_list = cleanList(soup_titles_parts)
    final_original_list = soup_titles_parts
    return final_cleaned_list, final_original_list


def get_articles_titles_LI():
    page_content = urllib.request.urlopen(urls[2])
    soup = BeautifulSoup(page_content, 'html.parser')

    soup_articles_titles = []
    soup_articles_titles.append(soup.find_all("h2"))
    soup_articles_titles.append(soup.find_all(class_="live-title"))

    soup_titles_parts = []

    for soup_delimiter in soup_articles_titles:
        for part in soup_delimiter:
            soup_titles_parts.append(part.get_text(strip=True))

    final_cleaned_list = cleanList(soup_titles_parts)
    final_original_list = soup_titles_parts
    return final_cleaned_list, final_original_list


def get_articles_titles_LH():
    page_content = urllib.request.urlopen(urls[3])
    soup = BeautifulSoup(page_content, 'html.parser')

    for ex in soup.find_all("h2", {"class": re.compile(r"(block__title block-title)|(element-invisible)|(pane-title)")}):
        ex.extract()
    soup_articles_titles = soup.find_all("h2")

    soup_titles_parts = []
    for part in soup_articles_titles:
        soup_titles_parts.append(part.get_text(strip=True))

    final_cleaned_list = cleanList(soup_titles_parts)
    final_original_list = soup_titles_parts
    return final_cleaned_list, final_original_list


def get_articles_titles_LE():
    page_content = urllib.request.urlopen(urls[4])
    soup = BeautifulSoup(page_content, 'html.parser')

    for ex in soup.find_all("div", {"class": re.compile(r"(meta-author)")}):
        ex.extract()
    soup_articles_titles = soup.find_all(class_="titre")

    soup_titles_parts = []
    for part in soup_articles_titles:
        soup_titles_parts.append(part.get_text(strip=True))

    final_cleaned_list = cleanList(soup_titles_parts)
    final_original_list = soup_titles_parts
    return final_cleaned_list, final_original_list


def upload_articles_titles(cleaned_titles, original_titles, journal_id):
    start_time = datetime.now()
    date_now = "{}-{}-{}".format(start_time.year, start_time.month, start_time.day)
    try:
        row_counts = 0
        for cleaned_title, original_title in zip(cleaned_titles, original_titles):
            cursor =  connection.cursor(buffered=True)
            sql = "SELECT cleaned_title FROM titles WHERE cleaned_title = %s"
            cursor.execute(sql, (cleaned_title,))

            if cursor.rowcount == 0:
                args = (journal_id, date_now, cleaned_title, str(original_title),)
                sql = "INSERT INTO titles (journal_id, dateScraped, cleaned_title, original_title) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, args)

                row_counts += cursor.rowcount
            cursor.close()
        return row_counts

    except Exception as e:
        logging.error(f"Error : {e}")

###
# The App
###
start_time = datetime.now()
date_now = "{}-{}-{}".format(start_time.year, start_time.month, start_time.day)

try:
    cleaned_list_LM, original_list_LM = get_articles_titles_LM()
    cleaned_list_LF, original_list_LF = get_articles_titles_LF()
    cleaned_list_LI, original_list_LI = get_articles_titles_LI()
    cleaned_list_LH, original_list_LH = get_articles_titles_LH()
    cleaned_list_LE, original_list_LE = get_articles_titles_LE()

except Exception as e:
    logging.critical(f"Error retrieving titles: {e}")
    sys.exit('Execution failed')

else:
    time_retrieved = datetime.now()
    logging.info(f"Titles retrieved in {time_retrieved - start_time}s")

    try:
        rows_inserted = 0
        rows_inserted += upload_articles_titles(cleaned_list_LM, original_list_LM, 1)

        rows_inserted += upload_articles_titles(cleaned_list_LF, original_list_LF, 2)
        rows_inserted += upload_articles_titles(cleaned_list_LI, original_list_LI, 3)
        rows_inserted += upload_articles_titles(cleaned_list_LH, original_list_LH, 4)
        rows_inserted += upload_articles_titles(cleaned_list_LE, original_list_LE, 5)

    except Exception as e:
        logging.critical(f"Error uploading titles in db: {e}")
        sys.exit('Execution failed')

    else:
        time_uploaded = datetime.now() - time_retrieved
        logging.info(f"{rows_inserted} Titles uploaded in {time_uploaded}s")

connection.close()