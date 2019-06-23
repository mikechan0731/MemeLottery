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


# ====== functions ===== #
# TODO
# 1. Special html type.
# 2. Check chapter list logic.
# 3. Check chapter sequence.
# 4. Check chapter name


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


    #find img tags
    img_tags = soup.find_all('img')
    count_nocomment = 1
    for img in img_tags:
        if img.parent.parent.name == "td":
            pass
        else:
            if img['src'].startswith('http') and img['src'].endswith('.jpg'):
                img_url = img['src']
                img_size = int(request.urlopen(img_url).info()['Content-Length'])
                img_type = "." + img_url.split(".")[-1]
                img_comment = ""
                img_name = date + "-" + chapter + "-n-" + "{:0>3d}".format(count_nocomment) + img_type
                count_nocomment += 1

                output_dict = { "img_name": img_name, 
                                "img_url": img_url, 
                                "img_size": img_size,
                                "img_comment": img_comment,
                                "img_date": date, 
                                "chapter": chapter, 
                                "owner": u"好色龍",
                            }
                memes_group.append(output_dict)
   
    tbody_tags = soup.find_all('tbody')
    count = 1
    for tbody in tbody_tags:
        if tbody.img and tbody.text:
            raw_url = tbody.img['src'].strip()
            if raw_url.startswith("http"):
                img_url = raw_url
            else:
                img_url = "https:" + raw_url

            img_size = int(request.urlopen(img_url).info()['Content-Length'])
            img_type = "." + img_url.split(".")[-1]
            img_comment = tbody.text.strip()
            img_name = date + "-" + chapter + "-" + "{:0>3d}".format(count) + img_type
            count += 1

            output_dict = { "img_name": img_name, 
                            "img_url": img_url, 
                            "img_size": img_size,
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

def create_sql(db_name="meme_lottery.db"):
    if os.path.exists(db_name):
        pass
    else:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE LOG(
            ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            LAST_UPDATE DATETIME,
            FID INTEGER
        );
        '''
        )
        c.execute('''CREATE TABLE MEMES(
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                IMG_NAME TEXT UNIQUE,
                IMG_URL TEXT UNIQUE,
                IMG_COMMENT TEXT,
                IMG_SIZE INTEGER,
                IMG_DATE DATETIME,
                CHAPTER INTEGER,
                OWNER TEXT,
                TAG TEXT,
                RANK INTEGER,
                PICK_DATE DATETIME,
                UPDATE_DATE DATETIME
            );
            '''
        )
        conn.commit()
        conn.close()

def push_memeinfo_to_sql(MEME_INFO):
    MEME_INFO = MEME_INFO
    conn = sqlite3.connect('meme_lottery.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO MEMES (IMG_NAME, IMG_URL, IMG_COMMENT, IMG_SIZE,\
                                  IMG_DATE, CHAPTER, OWNER)\
               VALUES (?,?,?,?,?,?,?)", 
        (MEME_INFO["img_name"], MEME_INFO["img_url"], MEME_INFO["img_comment"], 
         MEME_INFO["img_size"], MEME_INFO["img_date"], MEME_INFO["chapter"], 
         MEME_INFO["owner"])
    )
    conn.commit()
    conn.close()

def clear_sql_table(table_name):
    conn = sqlite3.connect('meme_lottery.db')
    c = conn.cursor()
    c.execute("DELETE FROM " + table_name)
    conn.commit()
    conn.close()
    print("Table " + table_name + " is clear.")

def update_and_push_all_to_sql(years_list):
    clear_sql_table('MEMES')
    for year in years_list:
        print("====={}=====".format(year))
        chapter_list = return_chapters_group_from_year(year)
        for chapter_url in chapter_list:
            memes_group = return_memeinfo_from_chapter_url(chapter_url)
            for meme_info in memes_group:
                push_memeinfo_to_sql(meme_info)
    print("Done.")

def main():
    years = ['2011','2012','2013','2014','2015','2016','2017','2018','2019']
    #years = ['2019']
    
    # ===== SQL Test
    create_sql()
    update_and_push_all_to_sql(years)

    # ===== Function Test
    #chapter_list = return_chapters_group_from_year()
    #rd_chapters = random.choice(chapter_list)
    #rd_memes = return_memeinfo_from_chapter_url(rd_chapters)
    #rd_memeinfo = random.choice(rd_memes)
    #push_memeinfo_to_sql(rd_memeinfo)
        
    #get_and_save(rd_memeinfo)

if __name__ == "__main__":
    main()
