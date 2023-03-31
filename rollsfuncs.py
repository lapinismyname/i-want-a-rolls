import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd

def extract(n): #this function is defined to make a proper search 
    if not " " in n:
        return str(n)
    else:
        k = ""
        while n[0] != " ":
            k += str(n[0])
            n = n[1:]
        return k + "-" + extract(n[1:])

def extract_price(n): #this function is defined to convert the price into an integer (ex: extract_price('250.000 TL') returns 250000)
    k = ""
    for i in n:
        if i != ".":
            k += i
        elif i == " ":
            break
    return int(k[:-3])
    
def bubble_sort(lst): #to sort the price_list
    swapped = True
    while swapped:
        swapped = False
        for n in range(len(lst) - 1):
            if lst[n][0] > lst[n + 1][0]:
                lst[n], lst[n + 1] = lst[n + 1], lst[n]
                swapped = True
    return lst     
        
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
    
def car_search(user_search):
    url = 'https://www.arabam.com/ikinci-el/'
    search = extract(user_search)
    document = requests.get(url + extract(search), headers = {'User-agent': 'your bot 0.1'}).text #accessing the website, converting it into a html document
    soup = BeautifulSoup(document, 'lxml') #cooking the soup    
    link = soup.find("meta", {"property": "al:web:url"}).get("content") #reaching the raw link to use it later 

    car_list = []
    null = ""
    #accumulate results for the first page
    page = 1
    next_page = link + '?take=50' #we want the page to display 50 elements per page)
    new_document = requests.get(next_page, headers = {'User-agent': 'your bot 0.1'}).text #BeautifulSoup phase
    new_soup = BeautifulSoup(new_document, 'lxml')
    price_list = new_soup.find_all("span", class_="db no-wrap listing-price")
    
    if not price_list: #error message
        return "no results found for '" + user_search + "', please make sure that all words are spelled correctly"

    dom = etree.HTML(str(new_soup))
    id_list = []
    ids = eval(new_soup.find("input", id="collect").get('value'))
    for i in ids:
        id_list += [i["advertId"]]
    model_list = new_soup.find_all("h3", class_="crop-after")

    for j in range(len(price_list)):
        price = price_list[j].get_text()[26:-22]
        price = extract_price(price)
        year = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[4]/div[1]/a')[0].text 
        if "minivan" in link: #the site displays results in a different way for vans
            km = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[6]/div[1]/a')[0].text[:-1]  
        else:
            km = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[5]/div[1]/a')[0].text[:-1]
        model = model_list[j].get_text()[1:-1]
        car_list.append([price, year, km, model])

    while dom.xpath('//*[@id="pagingNext"]/svg'): #continue accumulation until the next page button is clickable
        page += 1
        next_page = link + '?take=50&page=' + str(page) 
        new_document = requests.get(next_page, headers = {'User-agent': 'your bot 0.1'}).text 
        new_soup = BeautifulSoup(new_document, 'lxml')
        price_list = new_soup.find_all("span", class_="db no-wrap listing-price")

        dom = etree.HTML(str(new_soup))

        id_list = []
        ids = eval(new_soup.find("input", id="collect").get('value'))
        for i in ids:
            id_list += [i["advertId"]]
        model_list = new_soup.find_all("h3", class_="crop-after")

        for j in range(len(price_list)):
            price = price_list[j].get_text()[26:-22]
            price = extract_price(price)
            year = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[4]/div[1]/a')[0].text 
            if "minivan" in link:
                km = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[6]/div[1]/a')[0].text[:-1]  
            else:
                km = dom.xpath('//*[@id="listing' + str(id_list[j]) + '"]/td[5]/div[1]/a')[0].text[:-1]
            model = model_list[j].get_text()[1:-1]
            car_list.append([price, year, km, model])
    
    sorted_list = bubble_sort(car_list) #sort the prices to clean out outliers
    length = len(sorted_list)
    if length//2: #split the list into half to clean out left and right outliers
        first_half = new_first_half = sorted_list[:length//2]
        second_half = new_second_half = sorted_list[length//2:][::-1]
        for f in range(len(first_half) - 1):
            if first_half[f][0] * 5/2 <= first_half[f + 1][0]:
                new_first_half = new_first_half[1:]     
        for s in range(len(second_half) - 1):
            if second_half[s][0] >= second_half[s + 1][0] * 5/2:
                new_second_half = new_second_half[1:]           
        sorted_list = new_first_half + new_second_half[::-1]
    low_price, low_year, low_km, low_model = sorted_list[0][0], sorted_list[0][1], sorted_list[0][2], sorted_list[0][3]
    high_price, high_year, high_km, high_model = sorted_list[-1][0], sorted_list[-1][1], sorted_list[-1][2], sorted_list[-1][3]
    total, number = 0, len(sorted_list)
    for car in sorted_list:
        total += car[0]    
    average = total / number    
    if number == 1:
        result_text = " (over 1 result):"
    else:
        result_text = " (over " + str(number) + " results):"
            
    return [result_text, low_price, low_year, low_km, low_model, high_price, high_year, high_km, high_model, average]
        
def result_table(low_price, low_year, low_km, low_model, high_price, high_year, high_km, high_model, average): #return results with pandas
    dfs = pd.DataFrame(
        {
            "price": [dotter(low_price) + ' TL', dotter(high_price) + ' TL', dotter(int(average)) + ' TL'],
            "year": [low_year, high_year, ""],
            "km": [low_km, high_km, ""],
            "model": [low_model, high_model, ""]
            }
        ,index = ["lowest price", "highest price", "average price"])
    return dfs
    
#i want a rolls by lapin
#12.02.2023
