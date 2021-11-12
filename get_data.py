import pandas as pd
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import requests 
import re
from tqdm import tqdm
import pickle

head_url = "https://tn.wikipedia.org/wiki/Special:AllPages"
next_url = "https://tn.wikipedia.org/w/index.php?title=Special:AllPages&from=Kgaolo+ya+Legare+%28Botswana%29"
collect = {"url":[],"title":[],"content":[]}


def get_meta_data(head_url_here):
    page = urllib.request.urlopen(head_url_here)
    soup = BeautifulSoup(page, "lxml")
    
    list_objects = soup.find_all(name = 'li',)
    
    for k in range(len(list_objects)):
        try:
            yy = str(list_objects[k]).split("href=")[1].split("title")
            url = "https://tn.wikipedia.org" + yy[0].replace("\"","")
            title = yy[1].split(">")[1].split("<")[0]
            collect["url"].append(url)
            collect["title"].append(title)
        except Exception as e:
            print(e)


def pull_content(url):
    paraphs = ""
    
    try:
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        texts = soup.find_all('p',)
        
        for k in range(len(texts)):
            if str(texts[k]).find("Coordinates")==-1 and len(str(texts[k]))>3:
                s = str(texts[k])
                s = re.sub('<.*?>', '', s)
                s = re.sub('[[0-9]*?]','',s)
                if len(s.split(" "))>2:
                    paraphs = paraphs + s + " $$$$$ "
    except Exception as e:
        print(e)
    return paraphs
    
###############Pull urls  and titles#####################
get_meta_data(head_url)


del collect["url"][345:]       
del collect["title"][345:]

get_meta_data(next_url)

del collect["url"][690:]       
del collect["title"][690:]

#########################################################
#######################get content#######################

collect['content'] = []
language = "tswana"

for j in tqdm(range(len(collect['url']))):
    collect['content'].append(pull_content(collect['url'][j]))

final_frame = pd.DataFrame(collect)
final_frame.to_csv("%s_wiki.csv"%language)
file_pi = open('%s_wiki.pick'%language, 'wb') 
pickle.dump(final_frame, file_pi,pickle.HIGHEST_PROTOCOL)
file_pi.close()
###########################################################
####################Load from file#########################
file_pi = open('%s_wiki.pick'%language, 'rb') 
collect = pickle.load(file_pi)

###########################################################
def dirt(string):
    words = ["Template","Category",":Infobox"]
    chars = ["|","--","=","[[", "...", "&gt"," ·"]
    
    for k in words:
        string = string.replace(k,"")
    for k in chars:
        string = string.replace(k,"")
    
    return string.replace("\n", " ").replace("  "," ").replace(" -;",";").strip()
    
    
def training_sentences():
    s = list(map(dirt, collect["content"]))
    huge_sent = []
    with open("%s_wiki-clean.txt"%language,"wb") as f:
        for article in s:
            hold = article.split("$$$$$")
            for sent in hold:
                if len(sent)>3 and sent.find("format needs")==-1:
                    f.write((sent.strip()+"\n").encode("utf-8"))
                    huge_sent.append(sent.strip())
    f.close()
    return huge_sent

Pure_sentences = training_sentences()





