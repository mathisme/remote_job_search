#importing what is needed
import time
import pandas as pd
import requests
import json5
from datetime import date

url_base = 'https://www.indeed.com/jobs?l=remote&explvl=entry_level&fromage=1&limit=50'
jobs = []
err_count = 0
r = requests.get(url_base)
while r.status_code!=200 and err_count < 5:
    time.sleep(5)
    err_count = err_count + 1
    r = requests.get(url_base)
if err_count==5:
    quit()
text = r.text
for i in range(text.count('jobmap[')):
    start = text.find('jobmap[{}]'.format(i))
    if start==-1:
        continue
    end = text.find('jobmap[{}]'.format(i+1))
    s = text.find('{',start)
    if end == -1:
        e = text.find('}',s)
    else:
        e = text.rfind('}',s,end)
    job = json5.loads(text[s:e+1])
    jobs.append(job)

df = pd.DataFrame(jobs)
df.drop_duplicates(inplace=True)
df['job_link']='https://www.indeed.com/viewjob?jk='+df.jk
df.rename(columns={'cmp':'company'},inplace=True)
df = df[(df['country']=="US")&(df["loc"]=="Remote")].copy()
df = df[['title','company','job_link']].copy()
df.reset_index(inplace=True)
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
