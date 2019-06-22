#-*-coding: utf-8-*-
# editor: MikeChan
# email: m7807031@gmail.com
 
# OS import
import os, random
import sqlite3
from datetime import date

# Parser import 
import requests
from urllib import request
from bs4 import BeautifulSoup

#===== Global Variables


#===== Structure
# base_link-> years_group -> single_year -> chapters_group -> chapter -> memes_group -> meme_url  


def return_one_meme_url(url:str = 'http://hornydragon.blogspot.com/2019/06/1113.html'):
    target = url
    res = requests.get(target)
    soup = BeautifulSoup(res.text, "html.parser")
    page_content = []

    # page infomation
    title = soup.title.text.split(':')[1].strip()
    chapter = target.split('/')[-1].split('.')[0]
    raw_date = soup.find("abbr").text.strip().split(" ")[0].split("/")
    year = raw_date[2]
    if len(raw_date[0]) < 2: month =  "0" + raw_date[0]
    else: month = raw_date[0]
    if len(raw_date[1])<2: day = "0" + raw_date[1]
    else: day = raw_date[1]
    date = "{}-{}-{}".format(year, month, day)

    tbody_tags = soup.find_all('tbody')
    count = 1
    for tbody in tbody_tags:
        if tbody.img and tbody.text:
            img_url = "http://" + tbody.img['src']
            img_comment = tbody.text.strip()
            img_name = date + "-" + chapter + "-" + "{:0>3d}".format(count)
            count += 1
            output_dict = {"img_name":img_name, "img_url":img_url, "img_comment":img_comment, 
                           "img_date":date, "chapter": chapter, "owner": "hornydragon",
                           "tag":"", "rank": ""}
            page_content.append(output_dict)
    print("*** Meme number: " + str(len(page_content)))
    return page_content

def update_meme_urls():
    b_url='https://hornydragon.blogspot.com/'
    years = ['2011','2012','2013','2014','2015','2016','2017','2018', '2019']
    single_year_urls ={}
    All_YEAR_URLS = []
    for year in years:
        print( year + " is updating.")
        target = b_url + year + '/'
        res = requests.get(target)
        soup = BeautifulSoup(res.text, "html.parser")
       
        alllink_urls =[]
        almost_right_urls=[]

        #抓出網頁內所有連結
        a_tags = soup.find_all('a')
        for a in a_tags:
            if a.text.startswith(u'雜七雜八短篇'):
                alllink_urls.append(a['href'])

        #抓出所有連結開頭是好色龍網址, 結尾是.html
        for i in alllink_urls:
            if i.startswith('https://hornydragon.blogspot.com/') and i.endswith('.html'):
                almost_right_urls.append(i)

        single_year_urls = {"year": year, "chapters_urls": set(almost_right_urls)}
        All_YEAR_URLS.append(single_year_urls)

    return All_YEAR_URLS

def update_to_sql():
    ALL_MEMEs = []
    All_YEAR_URLS = update_meme_urls()
    #print(All_YEAR_URLS)

    for YEAR_DICT in All_YEAR_URLS:
        print("====={}=====".format(YEAR_DICT["year"]))
        #print(YEAR_DICT["chapters_urls"])
        chapter_count = 0
        for chapter_url in YEAR_DICT['chapters_urls']:
            chapter_count += 1
            print("Chapter " + str(chapter_count))
            memes_list = return_one_meme_url(chapter_url)
            for meme_info in memes_list:
                ALL_MEMEs.append(meme_info)
    return ALL_MEMEs        

def get_and_save(img_url):
    request.urlretrieve(img_url, "pics/%s" %img_url.split('/')[-1])

def create_sql():
    conn = sqlite3.connect('memes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE MEMES(
            ID INT PRIMARY KEY NOT NULL,
            IMG_NAME TEXT NOT NULL,
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

def push_to_sql(MEME_INFO):
    MEME_INFO = MEME_INFO
    conn = sqlite3.connect('memes.db')
    c = conn.cursor()
    c.execute("INSERT INTO MEMES (IMG_NAME, IMG_URL, IMG_COMMENT, \
                                  IMG_DATE, CHAPTER, OWNER, TAG, RANK)\
               VALUES ({0},{1},{2},{3},{4},{5},{6},{7})".format(
                   MEME_INFO["img_name"], MEME_INFO["img_url"], MEME_INFO["img_comment"],
                   MEME_INFO["img_date"], MEME_INFO["chapter"], MEME_INFO["owner"],
                   MEME_INFO["tag"], MEME_INFO["rank"] )
            )
    conn.commit()
    conn.close()


def main():
    create_sql()
    #ALL_MEMEs = update_to_sql()
    print("All meme's dictionary is ready.")
    
    for meme_info in ALL_MEMEs:
        print(i)
        push_to_sql(meme_info)



if __name__ == "__main__":
    main()


#===================reference
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





