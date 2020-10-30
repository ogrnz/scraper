# scraper
French journals title scraper

Scraping *experiment* in Python. 

The goal is here to scrape the titles of daily french newspaper from different political stances. The last uploaded database is from the October 30th 2020 (scrapper enabled on Augut 10, 2019). The .sql dump can be found in the repo and contains **65,665** entries. 

The data is raw. No stopwords were removed other than the punctuation (100% original data is available in the dump). 

List of scrapped journals (in journaux-orientation-pol.txt):
```
Le Monde : central left
Le Figaro : right
Libération : left
Les Echos : 'economical' right
L'Humanité : far-left
```

Ideas:
- conduct sentiment analysis on the titles, do the far-right journals cultivate fear more than the far-left?
- how long does a 'buzz' survive in the journals?
- conduct all kind of NLP experiments
- ...