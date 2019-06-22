# -*-coding: utf-8-*-
# editor: MikeChan
# email: m7807031@gmail.com

# OS import
import os
import random
import sqlite3
from datetime import date

# Parser import
import requests
from urllib import request
from bs4 import BeautifulSoup

# ===== Page Structure =====#
# base_link[years_group] -> single_year[chapters_group]
# -> single_chapter[memes_group] -> meme_info

# ===== Global Variables ===== #
years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

# ====== functions ===== #
def return_memeinfo_from_chapter_url(url="http://hornydragon.blogspot.com/2019/06/1116.html"):
    target = url
    res = requests.get(target)
    soup = BeautifulSoup(res.text, "html.parser")
    memes_group = []

    # page infomation
    title = soup.title.text.split(':')[1].strip()
    chapter = target.split('/')[-1].split('.')[0]
    raw_date = soup.find("abbr").text.strip().split(" ")[0].split("/")
    
    # date process 
    year = raw_date[2]
    if len(raw_date[0]) < 2:
        month = "0" + raw_date[0]
    else:
        month = raw_date[0]
    if len(raw_date[1]) < 2:
        day = "0" + raw_date[1]
    else:
        day = raw_date[1]
    date = "{}-{}-{}".format(year, month, day)

    tbody_tags = soup.find_all('tbody')
    count = 1
    for tbody in tbody_tags:
        if tbody.img and tbody.text:
            img_url = tbody.img['src']
            img_comment = tbody.text.strip()
            img_name = date + "-" + chapter + "-" + "{:0>3d}".format(count) + ".jpg"
            count += 1
            output_dict = { "img_name": img_name, 
                            "img_url": img_url, 
                            "img_comment": img_comment,
                            "img_date": date, 
                            "chapter": chapter, 
                            "owner": u"好色龍",
                           }
            memes_group.append(output_dict)
    print("chapter {0}, Meme number: {1}".format(chapter, str(len(memes_group))))
    return memes_group

# input sample: '2011', '2012' ... '2019'
def return_chapters_group_from_year(input_year:str='2016'):
    b_url = 'https://hornydragon.blogspot.com/'

    print("{}".format(input_year) + " is updating.")
    target = b_url + input_year + '/'
    res = requests.get(target)
    soup = BeautifulSoup(res.text, "html.parser")

    # get all link from url
    a_tags = soup.find_all('a')
    alllink_urls = []
    for a in a_tags:
        if a.text.startswith(u'雜七雜八短篇'):
            alllink_urls.append(a['href'])

    # get link which starts with hornydragon url, end with ".html"
    chapter_urls = []
    for i in alllink_urls:
        if i.startswith('https://hornydragon.blogspot.com/') and i.endswith('.html'):
            chapter_urls.append(i)
    return chapter_urls

def get_and_save(MEME_INFO):
    request.urlretrieve(MEME_INFO['img_url'], "pics/{}".format(MEME_INFO['img_name']))

def create_sql():
    conn = sqlite3.connect('meme_lottery.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE SUMMARY(
        ID INT PRIMARY KEY NOT NULL,
        YEAR DATETIME,
        LAST_UPDATE DATETIME,
        FID INT
    );
    '''
    )
    c.execute('''CREATE TABLE MEMES(
            ID INT PRIMARY KEY,
            IMG_NAME TEXT,
            IMG_URL TEXT,
            IMG_COMMENT TEXT,
            IMG_DATE DATETIME,
            CHAPTER INT,
            OWNER TEXT,
            TAG TEXT,
            RANK INT,
            PICK_DATE DATETIME,
            UPDATE_DATE DATETIME
        );
        '''
    )
    conn.commit()
    conn.close()

def push_memeinfo_to_sql(MEME_INFO, count):
    MEME_INFO = MEME_INFO
    conn = sqlite3.connect('meme_lottery.db')
    c = conn.cursor()
    c.execute("INSERT INTO MEMES (ID, IMG_NAME, IMG_URL, IMG_COMMENT, \
                                  IMG_DATE, CHAPTER, OWNER)\
               VALUES (?,?,?,?,?,?,?)", 
        (count, MEME_INFO["img_name"], MEME_INFO["img_url"], MEME_INFO["img_comment"],
        MEME_INFO["img_date"], MEME_INFO["chapter"], MEME_INFO["owner"])
    )
    conn.commit()
    conn.close()


def main():
    # ===== SQL Test
    #create_sql()
    
    # ===== Function Test
    chapter_list = return_chapters_group_from_year()
    rd_chapters = random.choice(chapter_list)
    rd_memes = return_memeinfo_from_chapter_url(rd_chapters)
    rd_memeinfo = random.choice(rd_memes)
    
    get_and_save(rd_memeinfo)
    #push_memeinfo_to_sql(rd_memeinfo, 1)
    


if __name__ == "__main__":
    main()


# ===================reference
'''
for i in meme_urls:
print(i)
print(requests.head(i).headers)

#將所有梗圖存入梗圖資料夾
for i in meme_urls:
request.urlretrieve(i, "%s\\%s_%s" %(title, chapter, i.split('/')[-1]))
print('%s is saved.'%(i))

#從 meme_list 隨機找一個丟出來
random_meme = random.choice(meme_urls)
if random_meme.startswith('//'):
random_meme = "https:" + random_meme

return(random_meme)
'''
