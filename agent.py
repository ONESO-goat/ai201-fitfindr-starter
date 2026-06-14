"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import traceback
from tools import FitFinder
from utils.data_loader import get_empty_wardrobe, save_chat_history
    

finder = FitFinder()

# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "chat": '',                  # Agents message towards the user
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
        "save_favorite": False       # If data was saved to favorites
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.
"""
    try:
        session = _new_session(query, wardrobe)
        response = finder.ai.generate_stylist_assistant(wardrobe=wardrobe, prompt=query)
        choices = finder.ai.background_helper(query)
        if not choices or not response:
            raise ValueError(f"Background helper or response failed: Choices: \n\t\u2022{choices} \ntyping: \n\t\u2022{type(choices)} response: \n\t\u2022{response}")
        search = None
        session['chat'] = response
        
        if choices['search_listings']:
            print("SEARCH LISTING...")
            session['search_listings'] = True
            search = finder.search_listings(choices['description'], choices['size'], choices['max_price'])
            session['selected_item'] = search[0]
            print("SEARCH LISTING COMPLETED")
            
        suggestion = ''
        if choices['suggest_outfit'] and search is not None:
            print("SUGGESTING OUTFIT...")
            session['suggest_outfit'] = True
            suggestion += finder.suggest_outfit(search[0], wardrobe=wardrobe)
            session['outfit_suggestion'] = suggestion
            print("SUGGUSTING OUTFIT COMPLETED")
        
        caption = ''    
        if choices['create_fit_card'] and suggestion:
            print("CREATING CAPTION...")
            session['create_fit_card'] = True
            caption = finder.create_fit_card(suggestion, search[0] if search else {})
            session['fit_card'] = caption
            print("CAPTION CREATION COMPLETED...")
            
        if choices['save_favorite']:
            session['save_favorite'] = True
            search = finder.save_favorite(suggestion, caption, new_item=search[0] if search else {}, type_=choices['save_favorite'])
            print("SAVED")
        
                
        return session
    except Exception as ex:
        print(f"There was an erorr while session process: \n\t\u2022{ex}")
        session["error"] = str(ex)
        traceback.print_exc()
        return session


# ── CLI test ──────────────────────────────────────────────────────────────────

def codepath_test():
        from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

        print("=== Happy path: graphic tee ===\n")
        session = run_agent(
            query="looking for a vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
        if session["error"]:
            print(f"Error: {session['error']}")
        else:
            print(f"Found: {session['selected_item']['title']}")
            print(f"\nOutfit: {session['outfit_suggestion']}")
            print(f"\nFit card: {session['fit_card']}")
        input("press ENTER to knowledge...")
        print("\n\n=== No-results path ===\n")
        session2 = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_empty_wardrobe(),
        )
        print(f"Error message: {session2['error']}")

def my_test():
    
    
        print("=== Happy path: graphic tee ===\n")
        session = run_agent(
            query="looking for a vintage graphic tee under $30",
            wardrobe=get_empty_wardrobe(),
        )
        if session["error"]:
            print(f"Error: {session['error']}")
        else:
            print(f"Found: {session['selected_item']['title']}")
            print(f"\nOutfit: {session['outfit_suggestion']}")
            print(f"\nFit card: {session['fit_card']}")
            
        input("\npress ENTER to knowledge...")
        print("\n\n=== No-results path ===\n")
        session2 = run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_empty_wardrobe(),
        )
        print(f"Error message: {session2['error']}")

def main():
    while True:
        
        user = input("Talk to the stylish general: ")
    
        
        if not user or not any(char.isalpha() for char in user):
            continue
        
        if user.lower().strip() in ['q', 'quit', 'break']:
            print('Leaving session, thanks for chatting with the stylist general')
            break
        
        session = run_agent(
            query=user,
            wardrobe=get_empty_wardrobe()['items'],
        )
        
        if session["error"]:
            print(f"Error: {session['error']}")
        else:
            
            print(f"Fashion general: \n\t\u2022{session['chat']}\n")
            print(f"Found: {session['selected_item']['title']}")
            print(f"\nOutfit: {session['outfit_suggestion']}")
            print(f"\nFit card: {session['fit_card']}")
            print(f"\nData saved: {session['save_favorite']}")
            save_chat_history(user=user, 
                              outfit_suggestion=session['outfit_suggestion'],
                              caption=session['fit_card'],
                              response=session['chat'], 
                              new_item=session['selected_item'], 
                              was_saved=session['save_favorite'])
        continue
        
if __name__ == "__main__":
    test = [
        "I am looking for a long sleeve shirt that's around $50 dollars, I am going out with some friends so I will be posting this on the media.",
        
        "I'm looking for a vintage graphic tee under $30, size M. I mostly wear baggy jeans and chunky sneakers. This will be for an event with family so I hope to remember this moment. Can you create a caption as I will be posting this online, Thanks!"
    
    ]
    
    main()