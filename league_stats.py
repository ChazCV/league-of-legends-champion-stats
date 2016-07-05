# -*- coding: utf-8 -*-
import re
import json

import requests
import wikia
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


"""Recurring abbreviations are as follows:
       df: pandas DataFrame
       hp: health points
       ar: armor
       mr: magic resistance
       eh: effective heatlh
       champ: League of Legends character
"""


def wikia_table_scraper(url): 
    """Extracts table data from League of Legends Wikia pages.
        
    returns: DataFrame containing all table data from given URL.
    """
    
    req = requests.get(url)
    data = req.json()
    soup = BeautifulSoup(data['content'], 'lxml')
    wikia_df = pd.DataFrame()

    for table in soup('table'):
        tag_count = 0
        head_count = 0
        col_vars = []
        rows = []
        row = []
        
        for heading in table('th'):
            col_vars.append(heading.get_text().strip())
            head_count += 1

        for tag in table('td'):
            if tag_count % head_count == 0:
                row.append(tag.span.get_text().strip())
                tag_count += 1

            else:
                row.append(tag.get_text().strip())
                tag_count += 1
                if tag_count % head_count == 0:
                    rows.append(row)
                    row = []
                    
        data = pd.DataFrame(data = rows, columns = col_vars)
        wikia_df = wikia_df.append(data)
    
    return wikia_df

    
def champions_df():
    """Returns DataFrame containing statistics for each individual
    champion.  Extracted from:
    http://leagueoflegends.wikia.com/wiki/Base_champion_statistics .
    """
    
    url = "http://leagueoflegends.wikia.com/api/v1/Articles/AsJson?id=2971"
    champ_df = wikia_table_scraper(url)
    champ_df.set_index('Champions', inplace=True)
    champ_df.index.names = ['Champion']
    champ_df['AS+'] = champ_df['AS+'].replace('%','',regex=True)
    champ_df['AS+'] = champ_df['AS+'].astype('float')/100
    champ_df = champ_df.astype(float)
    return champ_df

    
def items_df():
    """Returns DataFrame containig individual item attribute values.
    Extracted from:
    http://leagueoflegends.wikia.com/wiki/List_of_items%27_stats .
    """
    
    url = "http://leagueoflegends.wikia.com/api/v1/Articles/AsJson?id=1282521"
    item_df = wikia_table_scraper(url)
    item_df.set_index('Item', inplace=True)
    item_df.rename(columns={'Health': 'HP', 'Armor': 'AR'}, inplace=True)
    del item_df['Availability']
    item_df.replace('', np.nan, inplace=True)
    percent_stats = ['AS', 'CDR', 'Crit', 'HP5', 'Lifesteal', 'MP5']
    for col in percent_stats:
        item_df[col] = item_df[col].replace(r'\D', r'', regex=True)
        item_df[col] = item_df[col].astype(float) / 100
    item_df = item_df.astype(float).groupby(item_df.index).max()
    return item_df

    
def champ_growth_df(champ): 
    """Calls champions_df() and uses a specified champion's level 1 
    health, armor, and magic resistance values, along with the
    value increases per level, and calculates these values up to and
    including level 18.   
    """
  
    champ_vals = champions_df().loc[champ].to_dict()
    growth_stats = ['HP', 'HP5', 'MP', 'AD', 'AS', 'AR', 'MR']
    growth_df = pd.DataFrame(np.nan, index=range(1,19), columns=growth_stats)
    for stat in growth_stats:
        growth_df.ix[1, stat] = champ_vals[stat]
    for level in range(2, 19):        
        for stat in growth_stats:
            growth = stat + '+'
            champ_vals[stat] += champ_vals[growth]
        growth_df.ix[level] = champ_vals
    growth_df.index.name = 'Level'
    return growth_df

      
def leveled_with_items_stats(champ, level, *items):
    """Returns an individual champion's health, armor, and magic
    resitance for a given level and after accounting for the items
    in the champion's inventory.
    """
    
    champ_vals = champ_growth_df(champ).loc[level]
    item_df = items_df()    
    item_df = item_df.loc[[item for item in items]].sum()
    return (champ_vals + item_df).dropna()

    
def effective_health(champ, level, *items):
    """Takes a champion's total health, armor, and magic resistance,
    and calculates both their effective health against physical damage
    and their effective health against magic damage.
    """
    
    stat_totals = leveled_with_items_stats(champ, level, *items)
    hp, ar, mr = stat_totals[['HP', 'AR', 'MR']]
    ar_eh = hp * (1 + (ar / 100))
    mr_eh = hp * (1 + (mr / 100))
    return {'HP': hp, 'AR_EH': ar_eh, 'MR_EH': mr_eh}


def search_test(string_list, length=4):
    """Used primarily for testing purposes.
    Takes a list of strings, and, for each string, finds all
    substrings of the given length.  Occurences of each substring
    in the list of strings are saved to one of two lists: 
        seen: contains a single instance of each substring
        repeats: contains instances of each substring after their
            first occurence.
    """
    
    substrings = []
    for label in string_list:
        if len(label) >= length:
            substrings.append(label[0:length].lower())
            for i in range(0, len(label) - (length - 1)):
                substrings.append(label[i:i+length]) 
    seen = []
    repeats = []
    for string in substrings:
        if string not in seen:
            seen.append(string)
        else:
            repeats.append(string)
    return seen, repeats

    
def verify_name(name, dataframe):
    """Searches a DataFrame's index for a partial or full name.
    
    returns: name as it appears in the index.
    """
    
    df = dataframe.index
    header = df.name
    found = False
    while found == False:
        if not name:
            break
        else:
            
            name = name[0].upper() + name[1:]
            if name in df:
                found = True
                return name
            
            elif len(name) >= 4:
                substrings = [name[0:4].lower()]
                matches = set()
                for i in range(0, len(name) - 3):
                    substrings.append(name[i:i+4])                
                    for string in substrings:
                        for label in df:
                            if string in label:
                                matches.add(label)
                for match in matches:
                    verify = input('Did you mean {}? \n'
                                   '1) Confirm  \n'
                                   '2) Find next  \n'
                                   '3) Re-enter {} \n'
                                   .format(match, header.lower()))
                    if verify == '1':
                        found = True
                        return match
                    elif verify == '2':
                        continue
                    else:
                        name = input('Enter {} name or press Enter to cancel: '
                                     .format(header.lower()))                                 
                if len(matches) == 0:
                    name = input('{} not found. \n'
                                 'Re-enter {} or press Enter to cancel: '
                                 .format(header, header.lower()))                                                      
            
            else:
                name = input('{} not found. \n'
                             'Re-enter {} or press Enter to cancel: '
                             .format(header, header.lower()))


def verify_level():
    """Verifies that the user input for 'level' is an integer 
    between 1 and 18, inclusive.
    """
    
    while True:
        try:
            level = int(input('Enter a level between 1-18: '))
            if 19 > level > 0:
                return level
            else:
                print('Invalid level.')
                continue
        except ValueError:
            print('Invalid level.')
     
       
def main():
    """Asks the user for a champion, the champion's level, and up to 
    six inventory items. 
    
    returns: The total stats relevant to, and including, effective
    health.
    """
    
    champ = input('Enter a champion: ')
    champ = verify_name(champ, champions_df())
    level = verify_level()        
    if not champ:
        return None
    else:
        
        items = []
        item_count = 0      
        while item_count < 7:
            item = input('Enter an item or press Enter when finished: ')
            if not item:
                item_count += 7                
            else:
                item = verify_name(item, items_df())
                items.append(item)
                item_count += 1
                
    actual = leveled_with_items_stats(champ, level, *items)
    eh = effective_health(champ, level, *items)

    return print('\nChampion: {0:s} \n'
                 'Level: {1:g} \n'
                 'Health: {2:.2f} \n'
                 'Armor: {3:.2f} \n'
                 'Magic Resistance: {4:.2f} \n'
                 'Physical Effective Health {5:.2f} \n'
                 'Magical Effective Health {6:.2f} \n'
                 .format(champ, level, actual['HP'], actual['AR'],
                         actual['MR'], eh['AR_EH'], eh['MR_EH']))


if __name__ == "__main__":
    main()