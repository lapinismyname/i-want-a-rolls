import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import datetime

def extract(n): #this function is defined to make a proper search 
    if not " " in n:
        return str(n)
    else:
        k = ""
        while n[0] != " ":
            k += str(n[0])
            n = n[1:]
        return k + "-" + extract(n[1:])

url = 'https://www.arabam.com/ikinci-el/'
user_search = input()
search = extract(user_search)
document = requests.get(url + extract(search), headers = {'User-agent': 'your bot 0.1'}).text #accessing the website, converting it into a html document
soup = BeautifulSoup(document, 'lxml') #cooking the soup
link = soup.find("meta", {"property": "al:web:url"}).get("content")

#the page for the lowest price
low_document = requests.get(link + '?sort=priceTl.asc', headers = {'user-agent': 'your bot 0.1'}).text
low_soup = BeautifulSoup(low_document, 'lxml')

low_model = low_soup.find("h3", class_="crop-after") 

if low_model == None: #in case of wrong searches, print an error message
    print("no results found, please make sure that all words are spelled correctly")
    quit()
else:
    low_model = low_model.get_text()[1:-1]

low_listing, low_dom = low_soup.find("input", id="collect").prettify()[54:62], etree.HTML(str(low_soup))
low_price = low_dom.xpath('//*[@id="listing' + low_listing + '"]/td[7]/div[1]/a/span')[0].text[26:-22] #using xpath to access
low_year = low_dom.xpath('//*[@id="listing' + low_listing + '"]/td[4]/div[1]/a')[0].text

#the page for the highest price
high_document = requests.get(link + '?sort=priceTl.desc', headers = {'User-agent': 'your bot 0.1'}).text #the page for the highest price
high_soup = BeautifulSoup(high_document, 'lxml')

high_model = high_soup.find("h3", class_="crop-after").get_text()[1:-1]
high_listing, high_dom = high_soup.find("input", id="collect").prettify()[54:62], etree.HTML(str(high_soup))
high_price = high_dom.xpath('//*[@id="listing' + high_listing + '"]/td[7]/div[1]/a/span')[0].text[26:-22] #using xpath to access
high_year = high_dom.xpath('//*[@id="listing' + high_listing + '"]/td[4]/div[1]/a')[0].text

#the xpath's of kilometers are a bit different for vans, so determine whether the search was a van or not
if "minivan" in link:
    low_km = low_dom.xpath('//*[@id="listing' + low_listing + '"]/td[6]/div[1]/a')[0].text[:-1]
    high_km = high_dom.xpath('//*[@id="listing' + high_listing + '"]/td[6]/div[1]/a')[0].text[:-1]   
else:
    low_km = low_dom.xpath('//*[@id="listing' + low_listing + '"]/td[5]/div[1]/a')[0].text[:-1]
    high_km = high_dom.xpath('//*[@id="listing' + high_listing + '"]/td[5]/div[1]/a')[0].text[:-1]

def extract_price(n): #this function is defined to convert the price into an integer (ex: extract_price('250.000 TL') returns 250000)
    k = ""
    for i in n:
        if i != ".":
            k += i
        elif i == " ":
            break
    return int(k[:-3])

#accumulate results for the first page to forge an average price
page, number, total = 0, 0, 0
page += 1
next_page = link + '?take=50' #we want the page to display 50 elements per page)
new_document = requests.get(next_page, headers = {'User-agent': 'your bot 0.1'}).text #BeautifulSoup phase
new_soup = BeautifulSoup(new_document, 'lxml')
dom = etree.HTML(str(new_soup))
prices = new_soup.find_all("span", class_="db no-wrap listing-price")
for i in range(len(prices)):
    price = prices[i].get_text()[26:-22]
    price = extract_price(price)
    total += price
    number += 1

while dom.xpath('//*[@id="pagingNext"]/svg'): #continue until the next page button is clickable
    page += 1
    next_page = link + '?take=50&page=' + str(page)
    new_document = requests.get(next_page, headers = {'User-agent': 'your bot 0.1'}).text
    new_soup = BeautifulSoup(new_document, 'lxml')
    dom = etree.HTML(str(new_soup))
    prices = new_soup.find_all("span", class_="db no-wrap listing-price")
    for i in range(len(prices)):
        price = prices[i].get_text()[26:-22]
        price = extract_price(price)
        total += price
        number += 1
average = total / number

def dotter(n): #this function is defined to convert an integer to be represented in decimal notation (ex: extract_price('250000') returns 250.000)
    k = ""
    digit_count = 1
    digits = len(str(n))
    for i in str(n)[::-1]:
        digits -= 1
        if digits == 0:
            return (k + i)[::-1]
        elif digit_count == 3:
            k = k + i + "."
            digit_count = 1
        else:
            k += i
            digit_count += 1
    return k[::-1]

#result table
if number == 1:
    result_text = "results(over 1 result):"
else:
    result_text = "results(over " + str(number) + " results):"

dfs = pd.DataFrame(
        {
            "": ["lowest price", "highest price", "average price"],
            "price": [low_price, high_price, dotter(int(average)) + ' TL'],
            "year": [low_year, high_year, ""],
            "km": [low_km, high_km, ""],
            "model": [low_model, high_model, ""]
            }
        ,index = [1, 2, 3])

print("", result_text, dfs, "", sep='\n')
print("time:", "%s" % str(datetime.datetime.now())[:-10])
print("location: Turkey")
