
# Summary

league_stats.py asks the user for a League of Legends champion, the champion level, and the champion inventory. The champion's
health, armor, magic resistance, physical effective health, and magical effective health are returned.  

league_stats.ipynb includes the DataFrames used, and an introduction to a few of the methods that can be used to access and
compare the data.  

### Defining Effective Health:
Effective health is an alternative method for calculating a champion's defensive stats that ignores the concept of damage reduction and instead applies armor and magic resistance to separate health pools. Essentially, assume the enemy physical or magic damage is applied similar to true damage; an attack that deals 100 physical damage would remove 100 health from a champion's physical effective health pool. The effective health pools themselves are calculated thus:  
    Physical Effective Health Pool (PEH) = [HP x (100 + AR) / 100]  
    Magical Effective Health Pool (MEH) = [HP x (100 +MR) / 100]  
  
Physical effective health can be interpreted as taking a champion's total health and increasing it by 1% for every point of armor the champion has. For example, a champion with 2,000 HP and 40 AR has [2,000 x (100 + 40)/100] = 2,800 PEH; again, this is simply increasing the 2,000 HP by 1% for every one of the 40 points of armor. So with 2,000 HP and 40 AR, an enemy champion that deals a consistent 100 physical damage with auto attacks will need to attack the above champion a total of 28 times before killing them (this is ignoring health regen, shields, etc…). 

### Example


```python
import league_stats as lol
lol.main()
```

    Enter a champion: teemo
    Enter a level between 1-18: 15
    Enter an item or press Enter when finished: spirit
    Did you mean Spirit Visage? 
    1) Confirm  
    2) Find next  
    3) Re-enter item 
    1
    Enter an item or press Enter when finished: armor
    Did you mean Chalice of Harmony? 
    1) Confirm  
    2) Find next  
    3) Re-enter item 
    2
    Did you mean Warmog's Armor? 
    1) Confirm  
    2) Find next  
    3) Re-enter item 
    1
    Enter an item or press Enter when finished: abys
    Did you mean Abyssal Scepter? 
    1) Confirm  
    2) Find next  
    3) Re-enter item 
    1
    Enter an item or press Enter when finished: 
    
    Champion: Teemo 
    Level: 15 
    Health: 2963.76 
    Armor: 76.80 
    Magic Resistance: 145.00 
    Physical Effective Health 5239.93 
    Magical Effective Health 7261.21 
    
    
