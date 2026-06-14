"""
Utility functions for loading the mock listings dataset and wardrobe schema.
Use these in your tool implementations to access the data without re-reading
the files each time.
"""

import json
import os
from typing import Optional
from datetime import datetime, timezone

# Resolve the path to the data directory relative to this file
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_favorites(save:bool=False, data:dict={}, where_to_save='clothing'):
    """Loading the user's favoirtes"""
    
    path = os.path.join(_DATA_DIR, "favorites.json")
    with open(path, 'r') as file:
        favs = json.load(file)
    if save:
        if where_to_save not in ['clothing', 'outfits']:
            print(f"'{where_to_save}' is not a valid saving point")
            return favs
        if not data:
            print(f"Cant save an empty dataset")
            return favs
        
        favs[where_to_save].append(data)
        with open(path, 'w') as file:
            json.dump(favs,file, indent=4)
    return favs
    

def load_listings() -> list[dict]:
    """
    Load all mock listings from the dataset.

    Returns:
        A list of listing dictionaries. Each listing has the following fields:
        - id (str)
        - title (str)
        - description (str)
        - category (str): one of tops, bottoms, outerwear, shoes, accessories
        - style_tags (list[str])
        - size (str)
        - condition (str): excellent, good, or fair
        - price (float)
        - colors (list[str])
        - brand (str or None)
        - platform (str): depop, thredUp, or poshmark
    """
    path = os.path.join(_DATA_DIR, "listings.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_wardrobe_schema(save=False,data:dict={}) -> dict:
    """
    Load the wardrobe schema, including the example wardrobe and empty template.

    Returns:
        A dictionary containing:
        - schema: the field definitions for a wardrobe item
        - example_wardrobe: a sample wardrobe with 10 items
        - empty_wardrobe: a starting template for a new user
    """
    path = os.path.join(_DATA_DIR, "wardrobe_schema.json")
    with open(path, 'r') as file:
        war = json.load(file)
    if save:
        if not data:
            print(f"Cant save an empty dataset")
            return war
        
        war['empty_wardrobe']['items'].append(data)
        with open(path, 'w') as file:
            json.dump(war,file, indent=4)
    return war


def get_example_wardrobe(x:str='wardrobe') -> dict:
    """
    Convenience function — returns just the example wardrobe items list.

    Returns:
        A wardrobe dict with an 'items' key containing a list of wardrobe items.
    """
    if x in ['favorite', 'saved']:
        f = load_favorites() 
        return f['outfit_example']
    
    schema = load_wardrobe_schema()
    return schema["example_wardrobe"]


def get_empty_wardrobe() -> dict:
    """
    Convenience function — returns an empty wardrobe template.

    Returns:
        A wardrobe dict with an empty 'items' list.
    """
    schema = load_wardrobe_schema()
    return schema["empty_wardrobe"]


def save_chat_history(user, 
                      response,
                      caption, 
                      outfit_suggestion,
                      new_item=None, 
                      was_saved=False):
    try:
        path = os.path.join(_DATA_DIR, "history.json")
        with open(path, 'r') as file:
            history = json.load(file)
        
        h = {
            "id": len(history['chat_history']) + 1,
            "user": user,
            "response": response,
            "new_item": new_item,
            "outfit_suggestion": outfit_suggestion,
            "caption": caption,
            "saved": was_saved,
            "date": str(datetime.now(tz=timezone.utc)),
        }
        history['chat_history'].append(h)
        with open(path, 'w') as file:
            json.dump(history, file, indent=4)
        return True
    
    except Exception as ex:
        print(f"Chat was not saved: {ex}")
        return False

# --- Quick sanity check ---
if __name__ == "__main__":
    listings = load_listings()
    print(f"Loaded {len(listings)} listings.")
    print(f"First listing: {listings[0]['title']} — ${listings[0]['price']}")

    wardrobe = get_example_wardrobe()
    print(f"\nExample wardrobe has {len(wardrobe['items'])} items.")
    print(f"First item: {wardrobe['items'][0]['name']}")
