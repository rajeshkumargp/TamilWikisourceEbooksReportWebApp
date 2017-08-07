# -*- coding: utf-8 -*-
import sqlite3
import shutil 
import requests
import time
from time import gmtime, strftime

sqlite_file_Url  = "http://tools.wmflabs.org/wsexport/logs.sqlite"
#sqlite_file = wget.download(sqlite_file_Url) 

sqlite_file = sqlite_file_Url.split('/')[-1]
r = requests.get(sqlite_file_Url, stream=True)
with open(sqlite_file, 'wb') as f:
    for chunk in r.iter_content(chunk_size=1024): 
        if chunk:
            f.write(chunk)

#sqlite_file = 'data/logs.sqlite'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

overallDwndCount = 0 
timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

query = "SELECT TITLE,FORMAT,COUNT(*) as DWDCNT FROM CREATION where lang='ta' GROUP BY TITLE,FORMAT  ;"


outfile= open("report.csv","w")

aBookDetail = {}

allFormats = ["atom","epub","epub-2","epub-3","htmlz","mobi","odt","pdf",
            "pdf-a4","pdf-a5","pdf-a6","pdf-letter","rtf","txt","xhtml"]

aBookDetail["title"] = None
aCSVLine = "Title"
for aFormat in allFormats:
    aBookDetail[aFormat] = 0

aCSVLine = aCSVLine + ',' + ','.join([ aform 
                   for aform in allFormats]) + ",Total\n" 

outfile.write(aCSVLine)

c.execute(query)

ReportList = c.fetchall()
conn.close()

i = 1

for aline in ReportList: 
    booktitle,bookformat,bookcount = aline
    booktitle = booktitle.replace(",","")
    
    # Reading Very First Line and populating Dictionary
    if aBookDetail["title"] == None :
       
       aBookDetail["title"] = booktitle
       
       aBookDetail[bookformat] = bookcount
       
       aBookDetail["total"] = 0 
       aBookDetail["total"] =  aBookDetail["total"] + bookcount 
       
    #Reading Same book detail and populating Dictionary  
    elif aBookDetail["title"] ==  booktitle :
       aBookDetail[bookformat] = bookcount
       aBookDetail["total"] =  aBookDetail["total"] + bookcount 
       
    #Reading Differnt Book,Processing Dict Contents and Write to File
    else:
       aCSVLine = aBookDetail["title"]

       aCSVLine = aCSVLine + ',' + ','.join([ str(aBookDetail[aform]) 
                   for aform in allFormats]) + "," + str(aBookDetail["total"] )+"\n"
       # Write to a File
       #print(aCSVLine.encode('utf-8'))
       outfile.write(str(aCSVLine.encode('utf-8'))) 
   
       overallDwndCount = overallDwndCount + aBookDetail["total"]

       for aFormat in allFormats:
           aBookDetail[aFormat] = 0 
       aBookDetail["title"] = booktitle
    
       aBookDetail[bookformat] = bookcount
       aBookDetail["total"] = 0 
       aBookDetail["total"] =  aBookDetail["total"] + bookcount 
  
aCSVLine = aBookDetail["title"]
aCSVLine = aCSVLine +',' + ','.join([str(aBookDetail[aform]) 
             for aform in allFormats])+"," + str(aBookDetail["total"] )+"\n"

overallDwndCount = overallDwndCount + aBookDetail["total"]

# Writing Last Book Details
#print(aCSVLine)
outfile.write(str(aCSVLine.encode('utf-8')))
outfile.close()
shutil.move('logs.sqlite','data/logs.sqlite')
shutil.move('report.csv','data/report.csv')


total_time = open('data/time_total.html','w')
total_time.write('<link href="../css/bootstrap.min.css" rel="stylesheet">\n')
total_time.write("<p align='right'> இந்தப் பட்டியல் தினமும் ஒரு முறை இற்றைப்படுத்தப்படுகிறது. கடைசி இற்றை நேரம்   " + timestamp + " GMT  <br/>")
total_time.write(" மொத்தப் பதிவிறக்கங்கள் =   " + str(overallDwndCount) + "</p>")
total_time.close()

