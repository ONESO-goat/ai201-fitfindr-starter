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

    TODO — implement this function using the planning loop you designed in planning.md:

        Step 1: Initialize the session with _new_session().

        Step 2: Parse the user's query to extract a description, size, and
                max_price. You can use regex, string splitting, or ask the LLM
                to parse it — document your choice in planning.md.
                Store the result in session["parsed"].

        Step 3: Call search_listings() with the parsed parameters.
                Store results in session["search_results"].
                If no results: set session["error"] to a helpful message and
                return the session early. Do NOT proceed to suggest_outfit
                with empty input.

        Step 4: Select the item to use (e.g., the top result).
                Store it in session["selected_item"].

        Step 5: Call suggest_outfit() with the selected item and wardrobe.
                Store the result in session["outfit_suggestion"].

        Step 6: Call create_fit_card() with the outfit suggestion and selected item.
                Store the result in session["fit_card"].

        Step 7: Return the session.

    Before writing code, complete the Planning Loop and State Management sections
    of planning.md — your implementation should match what you described there.
    """
    # TODO: implement the planning loop
    
    try:
        session = _new_session(query, wardrobe)
        response = finder.ai.generate_stylist_assistant(query)
        choices = finder.ai.background_helper(query)
        if not choices or not response:
            raise ValueError(f"Background helper or response failed: Choices: \n\t\u2022{choices} \ntyping: \n\t\u2022{type(choices)} response: \n\t\u2022{response}")
        search = None
        session['chat'] = response
        if choices['search_listings']:
            session['search_listings'] = True
            search = finder.search_listings(choices['description'], choices['size'], choices['max_price'])
            session['selected_item'] = search[0]
            
        suggestion = ''
        if choices['suggest_outfit'] and search is not None:
            session['suggest_outfit'] = True
            suggestion += finder.suggest_outfit(search[0])
            session['outfit_suggestion'] = suggestion
        
        caption = ''    
        if choices['create_fit_card'] and suggestion:
            session['create_fit_card'] = True
            caption = finder.create_fit_card(suggestion, search[0] if search else {})
            session['fit_card'] = caption
            
        if choices['save_favorite']:
            session['save_favorite'] = True
            search = finder.save_favorite(suggestion, caption, new_item=search[0] if search else {}, type_=choices['save_favorite'])
            
        
                
        return session
    except Exception as ex:
        print(f"There was an erorr while session process: \n\t\u2022{ex}")
        session["error"] = str(ex)
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
        if user.lower().strip() in ['q', 'quit', 'break']:
            print('Leaving session, thanks for chatting with the stylist general')
            break
        
        if not user or not any(char.isalpha() for char in user):
            continue
        
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
                              caption=session['caption'],
                              response=session['chat'], 
                              new_item=session['selected_item'], 
                              saved=session['save_favorite'])
        continue
        
if __name__ == "__main__":
    main()