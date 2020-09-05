from flask import Flask, request, render_template, send_file, redirect, url_for
from requests import  get
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO


pages = [str(i) for i in range(0,100,20)]
jobtitle = []
company = []
location = []
date = []
link = []
searchjob="data analyst"
searchloc="Melbourne"

app = Flask(__name__)

@app.route('/')
def my_form():
	return render_template('my-form.html')


@app.route('/',methods=['POST'])
def my_form_post():
	searchjob = request.form['text']
	#processed_text = text.upper()
	
	searchloc = request.form['loc']
	
	for i in pages:
		response = get(f"https://au.indeed.com/m/jobs?q={searchjob}&l={searchloc}&start={pages}")
		html_soup = BeautifulSoup(response.text,'html.parser')
		jobtitle,company,location,date,link = get_job_titles(html_soup)
    
		data = {'jobtitle':jobtitle,'company':company,'location':location,'date posted':date,'link':link}
    
		df = pd.DataFrame(data)

	#df.to_excel('jobs_indeed.xlsx')

	output = BytesIO()

	#to download excel
	#Use the StringIO object as the filehandle.
	writer = pd.ExcelWriter(output, engine='openpyxl')
	df.to_excel(writer, sheet_name='jobs_indeed')
	writer.close()
	output.seek(0)

	return send_file(output, attachment_filename="jobs_indeed.xlsx", as_attachment=True)



def get_job_titles(html_soup):
    body = html_soup.find_all('body')
   
    for el in body[0].find_all('p'):
        if((el.h2 != None)and (el.find('span',class_='location')!=None) and (el.find('span',class_='date')!=None)):
            jobtitle.append(el.h2.text)
            company.append(el.text.split('\n')[1].split('-')[0])
            location.append(el.find('span',class_='location').text)
            date.append(el.find('span',class_='date').text)
            link.append('https://au.indeed.com/m/'+el.h2.a['href'])


    return jobtitle,company,location,date,link