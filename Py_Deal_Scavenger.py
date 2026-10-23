'''
This program is designed as a BOGO scraper that allows users to filter BOGOs based on location and item to item preferences
The program contains built in checks (via "______ passed" notifications) to make troubleshooting easier
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import bs4
import pandas
import smtplib
import re
from email.message import EmailMessage
import ssl
from rand_access_lib import gmailpass
import time
from datetime import date



#Scraping Prep
options = Options()
options.use_chromium = True
service = Service(executable_path=r"C:\Users\garne_2qwn9xv\Downloads\edgedriver_win64\msedgedriver.exe")
web_driver = webdriver.Edge(service = service, options = options)

def waitclick(path):
    try: 
         element = WebDriverWait(web_driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, path)))
         element.click()
    except Exception as e: 
        print(f"Error: {e}")
        time.sleep(5.0)
        waitclick(path)

web_driver.get('https://www.publix.com/savings/bogo?msockid=241258485b546c8d0e1a4d025a436da5')
waitclick('//*[@id="navBar"]/div/div[1]/div/button')

#Select Location
Location = input("What location would you like to pull from?\n")
    #search_bar sometimes doesn't work, could try defining another xpath to fix
search_bar = WebDriverWait(web_driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="navBar"]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/div/div[2]/div[2]/div/div/div/div[1]/form/input')))
search_bar.send_keys(Location + Keys.RETURN)
time.sleep(1.5)
'''
Store = [
    f'{web_driver.find_element(By.XPATH, '//*[@id="1061"]/div/div/div[1]/div[1]/h3').text}',
    f'{web_driver.find_element(By.XPATH, '//*[@id="776"]/div/div/div[1]/div[1]/h3').text}',
    f'{web_driver.find_element(By.XPATH, '//*[@id="1010"]/div/div/div[1]/div[1]/h3').text}'
    ]
Distance = [
    f'{web_driver.find_element(By.XPATH, '//*[@id="1061"]/div/div/div[1]/div[1]/div/span').text}',
    f'{web_driver.find_element(By.XPATH, '//*[@id="776"]/div/div/div[1]/div[1]/div/span').text}',
    f'{web_driver.find_element(By.XPATH, '//*[@id="1010"]/div/div/div[1]/div[1]/div/span').text}'
    ]
'''
Store = [
    web_driver.find_element(By.XPATH, '//*[@id="1061"]/div/div/div[1]/div[1]/h3').text,
    web_driver.find_element(By.XPATH, '//*[@id="776"]/div/div/div[1]/div[1]/h3').text,
    web_driver.find_element(By.XPATH, '//*[@id="1010"]/div/div/div[1]/div[1]/h3').text
]

Distance = [
    web_driver.find_element(By.XPATH, '//*[@id="1061"]/div/div/div[1]/div[1]/div/span').text,
    web_driver.find_element(By.XPATH, '//*[@id="776"]/div/div/div[1]/div[1]/div/span').text,
    web_driver.find_element(By.XPATH, '//*[@id="1010"]/div/div/div[1]/div[1]/div/span').text
]

select_store = int(input(
    "Please select a store\n"
    f"1 - {Store[0]} {Distance[0]:>50} \n"
    f"2 - {Store[1]} {Distance[1]:>50} \n"
    f"3 - {Store[2]} {Distance[2]:>50} \n"
    ))

if select_store == 1:
    waitclick('//*[@id="choose_1061"]')
elif select_store == 2:
    waitclick('//*[@id="choose_776"]')
elif select_store == 3:
    waitclick('//*[@id="choose_1010"]')
else:
    select_store = int(input('Please reinput choice'))

time.sleep(2.0)

print('Location Selection Passed')




#Load More
waitclick('//*[@id="main"]/div[5]/div/div[2]/div[2]/div[4]/button/span')
time.sleep(2.0)
try:
    load = web_driver.find_element(By.XPATH, '//*[@id="main"]/div[5]/div/div[2]/div[2]/div[4]/button/span')
    load.click()
except Exception:
    print('No more load button')

print('Load More Passed')



#Get and Filter BOGOs
html = web_driver.page_source
soup = bs4.BeautifulSoup(html, 'html.parser')

products = soup.findAll('span', {'class': 'p-text paragraph-md normal context--default color--null line-clamp title'})
print('Parsing Passed')

not_interested = {}
with open('not_interested.txt') as file :
    for line in file :
        key, bad_item = line.split()
        not_interested[int(key)] = bad_item
print('Filter Passed')

pub_deals = {}
for i in range(len(products)):
    product_text = products[i].get_text(strip=True)
    cleaned_text = re.sub(r'<>', '', product_text)
    if product_text not in not_interested.values():
        pub_deals[i] = [cleaned_text]

print('Data Gathering and Filtration Passed')




web_driver.quit()




pub_deals = pandas.DataFrame.from_dict(data = pub_deals, orient = 'index', columns=['Deal'])
print('Data Structuring Passed')



#Email Message
Subject = "Publix BOGOs " + date.today().strftime("%m%d")
Body = pub_deals.to_html(justify = 'center', col_space = 20)
eml = EmailMessage()

email_sender = "garnetteiv@gmail.com"
email_password = gmailpass
email_receiver = "garnetteiv@outlook.com"

eml["From"] = email_sender
eml["To"] = email_receiver
eml["Subject"] = Subject
eml.add_alternative(Body, subtype = 'html')

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as mp :
    mp.login(email_sender, email_password)
    mp.sendmail(email_sender, email_receiver, eml.as_string())
print('Email Passed')



exit()


#This program ultimately could be expanded to...
#  automatically tell what items are bogo or on good sales at Publix, Kroger, etc. and then compare the savings/cost 
#  calculate drive time/distance and then tell you the best grouping of items given gas cost (eg if only 1 bogo item at pub tells you go walmart but also show alt solution)
#  run in background and notify user when deals on desired items are out