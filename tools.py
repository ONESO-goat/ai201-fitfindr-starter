"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

from dotenv import load_dotenv
from typing import Union
from chatbot import Chatbot
from utils.data_loader import load_listings, load_favorites, load_wardrobe_schema

load_dotenv()

class FitFinder:
    def __init__(self, use_ollama:bool=False) -> None:
        self.ai: "Chatbot" = Chatbot(use_ollama=use_ollama)
        
    def size_choices(self):
        return ['xs', 'small', 's', 'medium', 'm', 'l', 'large', 'xl']
    
    # ── Groq client ───────────────────────────────────────────────────────────────

    # def _get_groq_client(self):
    #     """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    #     api_key = os.environ.get("GROQ_API_KEY")
    #     if not api_key:
    #         raise ValueError(
    #             "GROQ_API_KEY not set. Add it to a .env file in the project root."
    #         )
       
    #     return Groq(api_key=api_key)

    def filtering(self, listed, max_price, size):
        if not max_price and not size:
                return listed
            
        filt = None
        if max_price is not None:
            filt = [item for item in listed if item['price'] <= max_price]
        
        
    
        if not filt:
            filt = [item for item in listed if size in item['size']]
        else:
            f = []
            for item in filt:
                #print(f"ITEM: {item}")
                if size.lower().strip() in item['size'].lower():
                    f.append(item)
            return f
        return filt
        

    # ── Tool 1: search_listings ───────────────────────────────────────────────────

    def search_listings(
        self,
        description: str,
        size: str | None = None,
        max_price: float | None = None,
    ) -> list[dict]:
        """
        Search the mock listings dataset for items matching the description,
        optional size, and optional price ceiling.

        Args:
            description: Keywords describing what the user is looking for
                        (e.g., "vintage graphic tee").
            size:        Size string to filter by, or None to skip size filtering.
                        Matching is case-insensitive (e.g., "M" matches "S/M").
            max_price:   Maximum price (inclusive), or None to skip price filtering.

        Returns:
            A list of matching listing dicts, sorted by relevance (best match first).
            Returns an empty list if nothing matches — does NOT raise an exception.

        Each listing dict has the following fields:
            id, title, description, category, style_tags (list), size,
            condition, price (float), colors (list), brand, platform

        TODO:
            1. Load all listings with load_listings().
            2. Filter by max_price and size (if provided).
            3. Score each remaining listing by keyword overlap with `description`.
            4. Drop any listings with a score of 0 (no relevant matches).
            5. Sort by score, highest first, and return the listing dicts.

        Before writing code, fill in the Tool 1 section of planning.md.
        """
        # Replace this with your implementation
        
        listed = load_listings()

        filtered = self.filtering(listed, max_price, size)

        final_list = []  
        for item in filtered:
            score = self.ai.generate_scoring(description=description, item=item)
            if not isinstance(score, Union[int, float]):
                raise ValueError(f"Score wasn't returned as an Int or Float: Returned: \n\t\u2022{score} \nType: \n\t\u2022 ({type(score)}) \nplease double data")
            
            if int(score) <= 0:
                continue
            
            item['score'] = score
            final_list.append(item)
            
        return sorted(final_list, key=lambda d: d['score'], reverse=True)


    # ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

    def suggest_outfit(self,new_item: dict, wardrobe: dict={}) -> str:
        """
        Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

        Args:
            new_item: A listing dict (the item the user is considering buying).
            wardrobe: A wardrobe dict with an 'items' key containing a list of
                    wardrobe item dicts. May be empty — handle this gracefully.

        Returns:
            A non-empty string with outfit suggestions.
            If the wardrobe is empty, offer general styling advice for the item
            rather than raising an exception or returning an empty string.

        TODO:
            1. Check whether wardrobe['items'] is empty.
            2. If empty: call the LLM with a prompt for general styling ideas
            (what kinds of items pair well, what vibe it suits, etc.).
            3. If not empty: format the wardrobe items into a prompt and ask
            the LLM to suggest specific outfit combinations using the new item
            and named pieces from the wardrobe.
            4. Return the LLM's response as a string.

        Before writing code, fill in the Tool 2 section of planning.md.
        """
         # this function already does most of the documented task
        response = self.ai.generate_stylist_assistant(new_outfit=new_item)
        
        if not response:
            raise ValueError(f"Inside suggest_outfit, the agent's response returned invalid text: {response}")
        
        return response


    # ── Tool 3: create_fit_card ───────────────────────────────────────────────────

    def create_fit_card(self, outfit: str, new_item: dict) -> str:
        """
        Generate a short, shareable outfit caption for the thrifted find.

        Args:
            outfit:   The outfit suggestion string from suggest_outfit().
            new_item: The listing dict for the thrifted item.

        Returns:
            A 2–4 sentence string usable as an Instagram/TikTok caption.
            If outfit is empty or missing, return a descriptive error message
            string — do NOT raise an exception.

        The caption should:
        - Feel casual and authentic (like a real OOTD post, not a product description)
        - Mention the item name, price, and platform naturally (once each)
        - Capture the outfit vibe in specific terms
        - Sound different each time for different inputs (use higher LLM temperature)

        TODO:
            1. Guard against an empty or whitespace-only outfit string.
            2. Build a prompt that gives the LLM the item details and the outfit,
            and asks for a caption matching the style guidelines above.
            3. Call the LLM and return the response.

        Before writing code, fill in the Tool 3 section of planning.md.
        """
        t = f"""
        create A 2–4 sentence string usable as an Instagram/TikTok caption for this outfit I just created,
        The caption should:
        - Feel casual and authentic (like a real OOTD post, not a product description)
        - Mention the item name, price, and platform naturally (once each)
        - Capture the outfit vibe in specific terms
        - Sound different each time for different inputs (use higher LLM temperature):
        
        Outfit description:
        
        \u2022{outfit}
        """
        
        response = self.ai.generate_stylist_assistant(prompt=t, new_outfit=new_item)
        if not response:
            raise ValueError(f"Inside create_fit_card, the agent's response returned invalid text: {response}")
        
        return response
    
    def add_to_wardrobe(self, item:dict):
        try:
            load_wardrobe_schema(save=True, data=item) 
            return True
        except Exception as ex:
            print(f"Error occured while trying to add new item tpo wardrobe: \n\t\u2022{ex}\n")
            input("press ENTER to knowledge")
            return False
        
    def save_favorite(self, outfit:str, caption:str, new_item:dict, type_:str='clothing'):
        try:
            self.add_to_wardrobe(new_item) # assuming the user 'bought' the item
            new_item['caption'] = caption
            new_item['description'] = outfit
            load_favorites(save=True, data=new_item, where_to_save=type_)
            return True
        except Exception as ex:
            print(f"Error occured while trying to save new dataset: \n\t\u2022{ex}\n")
            input("press ENTER to knowledge")
            return False
        
        
        
    


if __name__ in "__main__":
    import logging
    logger = logging.getLogger(__name__)
    finder = FitFinder()
    test = {
    "id": "lst_040",
    "title": "Tie-Dye Long Sleeve — Pastel",
    "description": "Hand tie-dyed long sleeve in soft pastel hues — pink, lavender, and mint. Oversized unisex fit. 100% cotton.",
    "category": "tops",
    "style_tags": ["tie-dye", "cottagecore", "colorful", "streetwear"],
    "size": "L/XL",
    "condition": "excellent",
    "price": 17.00,
    "colors": ["pink", "lavender", "mint"],
    "brand": None,
    "platform": "depop"
  }
    #finder.search_listings(description='Loose silk', max_price=60.0, size='m')
    
    logger.info("=========================")
    logger.info(f"CREATING OUTFIT DATA...")
    logger.info("=========================")
    outfit = finder.suggest_outfit(new_item=test)
    print(f"1. OUTFIT: \n\t\u2022 {outfit}\n")
    
    logger.info("=========================")
    logger.info(f"CREATING CAPTION CARD...")
    logger.info("=========================")
    caption = finder.create_fit_card(outfit=outfit, new_item=test)
    print(f"2. CAPTION: \n\t\u2022 {caption}\n")
    
    logger.info("=========================")
    logger.info(f"SAVING OUTFIT DATA...")
    logger.info("=========================")
    saved = finder.save_favorite(outfit=outfit, new_item=test, caption=caption)
    
    

    print(f"3. WAS SAVED: \n\t\u2022 {saved}\n")