#importing what is needed
from datetime import date
import time
import pandas as pd
import requests
import json5
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# hide warnings
import warnings
warnings.filterwarnings('ignore')
opt = Options();
opt.add_argument("headless");
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)
url_base= 'https://www.indeed.com/jobs?l=remote&explvl=entry_level&fromage=7'
driver.get(url_base)
driver.implicitly_wait(0.5)
job_count = driver.find_element(By.ID, "searchCountPages")
job_count = job_count.text
job_count = job_count[job_count.find('of')+3:job_count.find('jobs')-1]
loc = job_count.find(',')
while loc != -1:
    job_count = job_count.replace(',','')
    loc = job_count.find(',')
job_count = int(job_count)
driver.quit()
jobs = []
for pg in range(min(job_count//50+1,4)):
    err_count = 0
    url = url_base+'&start={}&limit=50'.format(pg*50)
    r = requests.get(url)
    while r.status_code != 200 and err_count < 5:
        time.sleep(5)
        err_count += 1
        r = requests.get(url)
    for i in range(50):
        start = r.text.find('jobmap[{}]'.format(i))
        if start==-1:
            continue
        end = r.text.find('jobmap[{}]'.format(i+1))
        s = r.text.find('{',start)
        e = r.text.find('}',s)+1
        job = r.text[s:e]
        p = job.find(': ')
        while p != -1:
            job = job.replace(': ',':')
            p = job.find(': ')
        job = json5.loads(job)
        jobs.append(job)
    time.sleep(5)
df = pd.DataFrame(jobs)
df.drop_duplicates(inplace=True)
df['job_link']='https://www.indeed.com/viewjob?jk='+df.jk
df.rename(columns={'cmp':'company'},inplace=True)
df = df[df['country']=="US"].copy()
df = df[['title','company','job_link']].copy()
html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>Remote jobs</title>
</head>
<body>
<h1>Remote job listings</h1>
<ul>
"""
html_end = """
</ul>
</body>
</html>
"""
for i in range(df.shape[0]):
    line = '<li><a href="{}">{}: {}</a></li>'.format(df.loc[i,'job_link'], df.loc[i,'company'], df.loc[i,'title'])
    html += line
html+=html_end
file_name = "remote_jobs_{}.html".format(str(date.today()).replace('-',''))
with open(file_name,'w') as file:
    file.write(html)
