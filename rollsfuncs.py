import requests
import lxml.html as lh
import pandas as pd
from threading import Thread

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
    
def undotter(n):
    k = ""
    for i in n:
        if i == ".":
            continue
        else:
            k += i
    return int(k)
    
def page_search(link, page, car_list):
    link = link + '?take=50&page=' + str(page) #we want the page to display 50 elements per page
    page = requests.get(link, headers = {'User-agent': 'your bot 0.1'}) #accessing the link
    document = lh.fromstring(page.content) #parsing
    listings = document.find_class("listing-list-item pr") #get the list of attributes of the listings
    price_list = document.find_class("listing-price") #get the list of prices of the listings
    for j in range(len(listings)): #extract the information of attributes and prices to put them in a proper list
        price = extract_price(price_list[j].text_content()[26:-22])
        year = listings[j][3].text_content()[24:-26]
        if "minivan" in link: #the site displays results in a different way for vans
            km = listings[j][5].text_content()[40:-51]
        else:
            km = listings[j][4].text_content()[40:-51]
        model = listings[j][1].text_content()[24:-36]
        car_list.append([price, year, km, model])
    
def car_search(user_search):
    url = 'https://www.arabam.com/ikinci-el/'
    link = url + extract(user_search)
    page = requests.get(link, headers = {'User-agent': 'your bot 0.1'}) #accessing the website, converting it into an html document
    document = lh.fromstring(page.content) #parsing
    advert_number = document.get_element_by_id("js-hook-for-advert-count").text_content() #find how many adverts in the search
    
    if not eval(advert_number): #error message
        return "no results found for '" + user_search + "', please make sure that all words are spelled correctly"

    pages = undotter(advert_number) // 50 + 1
    if (pages > 1):
        link = document.xpath("//meta[@property='al:web:url']/@content")[0] #reaching the raw link to use it later
        if pages > 50:
            pages = 50

    car_list = []
    threads = []
    #using threads to send requests and parse the html documents concurrently
    for i in range(pages):
        threads.append(Thread(target=page_search, args=[link, i+1, car_list], daemon=True))
        threads[i].start()
    for i in range(pages):
        threads[i].join()

    sorted_list = bubble_sort(car_list) #sort the prices to clean out outliers
    length = len(sorted_list)
    if length//2: #split the list into half to clean out left and right outliers
        first_half = new_first_half = sorted_list[:length//2]
        second_half = new_second_half = sorted_list[length//2:][::-1]
        for f in range(len(first_half) - 1):
            if first_half[f][0] * 5/2 <= first_half[f + 1][0]:
                new_first_half = first_half[f+1:]
        for s in range(len(second_half) - 1):
            if second_half[s][0] >= second_half[s + 1][0] * 5/2:
                new_second_half = second_half[s+1:]           
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