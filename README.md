# i want a rolls
#### secondhand car prices

'i want a rolls' is a program that is used to access the prices and the superficial qualities of a car series quickly, according to the user's search.

The program inspects online ads and displays the collected data. There may be errors since the ads can be erroneous depending on the human mistakes.   

To run the program, one might want to install the modules first, if they're not already installed. To do this, run the commands below on your terminal:
```
$ pip install beautifulsoup4
$ pip install lxml
$ pip install pandas
```
#### Sample Run: 
```
$ python3 rolls.py
rolls royce ghost

results(over 9 results):
                          price  year      km                  model
1   lowest price  13.000.000 TL  2012  29.000  Rolls-Royce Ghost 6.6
2  highest price  36.500.000 TL  2022   6.001  Rolls-Royce Ghost 6.6
3  average price  18.238.888 TL                                     

time: 2023-02-06 15:59
location: Turkey               
```
