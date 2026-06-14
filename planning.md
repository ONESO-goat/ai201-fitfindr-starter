# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:** Searches the clothing listings database using a user's description, size preferences, and budget constraints to find matching items.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Natural language description of the item the user wants (e.g., "vintage graphic tee").
- `size` (str): User's preferred clothing size.
- `max_price` (float): Max price the user is willing to pay.

**What it returns:**
A list of matching clothing items containing its:

 - item name
 - category
 - size
 - price
 - description
<!-- Describe the return value — what fields does a result contain? -->

**What happens if it fails or returns nothing:**
Return a message explaining that no matching listings were found and suggest adding more details (different size, higher budget, or less specific description).

---

### Tool 2: suggest_outfit

**What it does:** 
Generates outfit recommendations by combining a newly found clothing item with pieces from the user's wardrobe or find different combination in the user's already existing wardrobe.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The clothing item selected from search results, this can be optional.
- `wardrobe` (dict): User's saved wardrobe.

**What it returns:**
An outfit recommendation containing:

 - top
 - bottom
 - shoes
 - accessories (optional)
 - styling explanation
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
If the wardrobe is empty or no compatible outfit can be generated, return styling suggestions that use only the new item and provide general recommendations.
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

returned data from suggest_outfit:

   
     • It seems like your wardrobe is empty, but that's totally okay. 
     We can fresh and build a brand new wardrobe that fits your personal style.

     To get started, can you tell me a bit about your fashion taste? Do you have a preference for classic and timeless pieces or do you like to stay on top of the latest trends? Are there any specific colors, patterns, or styles that you particularly enjoy wearing?

     Also, what's your lifestyle like? Are you more of a casual, laid-back person or do you have a job that requires you to dress up frequently? This will help me get a better idea of what types of clothing would be a good fit for you.

     Lastly, what's your budget like? Are you looking to invest in a few high-quality, timeless pieces or do you want to build a wardrobe on a more affordable budget?

     Let's chat, and I'll start making some recommendations based on your input. 

     Since you just got the "Silk Button-Down — Sage Green", I can give you some general styling advice on how to wear it. This top is perfect for a flowy, effortless look. You can pair it with some distressed denim jeans and sneakers for a casual, everyday look, or dress it up with a flowy skirt and some heeled sandals for a more elegant look. The sage green color is also really versatile, so you can easily pair it with neutrals like beige, black, or white, or add some contrast with brighter colors like yellow or orange. 

     Let me know if you have any other questions or if there's anything else I can help you with!
---

### Tool 3: create_fit_card

**What it does:**
Creates a final presentation card that summarizes the recommended outfit.

**Input parameters:**

- `outfit` (...): Complete outfit recommendation generated from the function 'suggest_outfit'.

**What it returns:**
A formatted fit card containing:

 - outfit title
 - clothing pieces
 - style description
 - estimated total cost
 - styling notes

**What happens if it fails or returns nothing:**
Return a simplified text summary to notify the user that a fit card could not be generated.
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

### Tool 4: save_favorite

**What it does:**
Allows users to save listings or outfit recommendations for future reference.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**

item_id (str): Unique identifier for the clothing item or outfit.
user_id (str): User identifier.

**What it returns:**
Confirmation that the item was successfully saved.

**What happens if it fails or returns nothing:**
Return an error message and allow the user to retry.

---

## Tool 5: save_history

**What it does:**
Saves the session history in a .json file.

**Input parameters:**

user: The user's text.
response: The agents response.
new_item: The new item provided from search_listings.
outfit_suggestion: The outfit suggestion for suggest_outfit.
caption: The caption from create_fit_card.



**What it returns:**
confirmation if it saved.

**What happens if it fails or returns nothing:**
Return a warning message indicating that the session
could not be saved. Continue the conversation without
interrupting the user experience.

## Planning Loop

**How does your agent decide which tool to call next?**
1. Analyze the user's request.

2. If the request contains clothing preferences
(description, size, category, budget),
call search_listings.

3. Check search results:
   - If results exist, store them in session state.
   - If no results exist, stop workflow and
     suggest broader criteria.

4. If the user selects an item OR the agent
chooses the highest-ranked result:
   - Check whether wardrobe data exists.
   - If wardrobe data exists, call suggest_outfit.
   - If wardrobe data does not exist, call
     suggest_outfit with an empty wardrobe.

5. Check outfit recommendation:
   - If an outfit is generated, store it.
   - If outfit generation fails, return styling
     suggestions using only the selected item.

6. Call create_fit_card using the generated outfit.

7. If the user requests saving:
   - Call save_favorite.
   - Call save_history.

8. Return the final fit card.

---

## State Management

**How does information from one tool get passed to the next?**
The planning loop stores state in a session dictionary.

Example:

session_state =       
     {
        "query": ...,              # original user query
        "chat": ...,                  # Agents message towards the user
        "parsed": {...},                # extracted description / size / max_price
        "search_results": [...,]        # list of matching listing dicts
        "selected_item": ...,       # top result, passed into suggest_outfit
        "wardrobe": ...,        # user's wardrobe dict
        "outfit_suggestion": ...,   # string returned by suggest_outfit
        "fit_card": ...,            # string returned by create_fit_card
        "error": ...,               # set if the interaction ended early
        "save_favorite": ...       # If data was saved to favorites
     }
The selected_item returned from search_listings is
saved in session_state and passed directly into
suggest_outfit.

Chat is the returned response from the agent.

The outfit returned from suggest_outfit is saved in
session_state and passed directly into create_fit_card.

This allows tools to share information without asking
the user to re enter it.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Inform user and suggest broader search criteria|
| suggest_outfit | Wardrobe is empty | Recommend outfit ideas using only the new item|
| create_fit_card | Outfit input is missing or incomplete |Return a text-based outfit summary |
| save_favorite | Save operation fails | Display error and allow retry |
---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
flowchart TD
    A[User Input] --> B[Planning Loop]

    B --> C[search_listings]
    C --> D[Search Results]

    D --> E[suggest_outfit]
    E --> F[Outfit Recommendation]

    F --> G[create_fit_card]
    G --> H[Final Fit Card]
    H --> I[User Output]

    D <--> J[Session State]
    F <--> J

    C --> K[No Results]
    K --> I

    E --> L[Wardrobe Empty]
    L --> I

    G --> M[Incomplete Outfit]
    M --> I
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
search_listings

AI Tool: Groq or Gemini
Input: Tool specification from planning.md
Output: Python function that filters listings based on description, size, and price
Verification: Test with multiple search queries and ensure filters work correctly

**Milestone 4 — Planning loop and state management:**
AI Tool: None (copilot maxed out for the month)
Input: Tool specification and outfit recommendation requirements
Output: Function that combines wardrobe items with a selected listing
Verification: Test with sample wardrobes and confirm sensible outfit recommendations
---

**Milestone 5 — create_fit_card**

AI Tool: Groq

Input:
- Tool 3 specification
- new Item

Output:
- Python function that generates a formatted fit card/social media styled caption

Verification:
- Test with complete outfits
- Test with missing accessories
- Test with incomplete outfit data and verify fallback text summary is returned

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
Agent calls:

search_listings(
    description="vintage graphic tee",
    size="M",
    max_price=30.00
)

Returns:
 - list of dicts
[{Vintage Band Tee ($25)},

{Retro Racing Tee ($28)}]

**Step 2:**
Agent selects the best matching item and calls:

suggest_outfit(
    new_item=Vintage Band Tee,
    wardrobe={
        "pants": ["Baggy Jeans"],
        "shoes": ["Chunky Sneakers"]
    }
)

Returns:

{    "id": uuid.UUID,
     "shirt": Vintage Band Tee,
     "pants": Baggy Jeans,
     "shoes": Chunky Sneakers,
     "accessory": Silver Chain Accessory
}

**Step 3:**
Agent calls:

create_fit_card(outfit, save=False)

Returns a formatted fit card with outfit details and styling notes.

if save is True, the Agent calls 'save_favorite' which saves the combo with  unique id (uuid or just a normal int)

**Final output to user:**

Fashion general: 
        Response from the agent.

Found: Item that was found in search_listing.

Outfit: Outfit created from suggest_outfit.

Fit card: Caption created from create_fit_card.

Data saved: True or False statment if data was saved into favorites.



EXAMPLE:
     user: I'm looking for a vintage graphic tee under $30, size M. I mostly wear baggy jeans and chunky sneakers.
     
     Fashion general: 
        •I'm happy to help you find a vintage graphic tee that fits your style and budget. Unfortunately, I couldn't find any vintage graphic tees in our current inventory that match your criteria of being under $30 and size M.

However, I can suggest some alternatives that might interest you. Since you mentioned you like to wear baggy jeans and chunky sneakers, I think a vintage-inspired graphic tee would be a great addition to your wardrobe.

Based on your favorite outfit, the Tie-Dye Long Sleeve — Pastel, I notice that you seem to enjoy unique and eye-catching pieces. I'd like to recommend checking out some other tie-dye or vintage-inspired tops that might pair well with your baggy jeans and chunky sneakers.

In our available clothing, we have the Vintage Levi's 501 Jeans — Medium Wash, which could be a great pairing with a graphic tee. The classic, vintage look of the jeans would provide a nice contrast to a more playful, graphic top.

If you're interested, I can also suggest some other items that might complement your style. For example, we could look for a black or white graphic tee with a fun design that would match your chunky sneakers and baggy jeans.

To better understand your preferences, could you tell me:

* Are you open to considering other styles or colors besides vintage graphic tees?
* Do you have a specific brand or style in mind for the graphic tee?
* Would you like me to suggest some other items that might pair well with your baggy jeans and chunky sneakers?

Let me know, and I'll do my best to provide you with some personalized recommendations!

Found: Y2K Baby Tee — Butterfly Print

Outfit: Since you've recently acquired the "Y2K Baby Tee — Butterfly Print" and have the "Tie-Dye Long Sleeve — Pastel" in your wardrobe, I'd love to suggest some outfit combinations that incorporate both pieces.

Considering the whimsical and vintage vibe of both tops, here are a few ideas:

1. **Layered Look**: Wear the "Y2K Baby Tee — Butterfly Print" under the "Tie-Dye Long Sleeve — Pastel" to create a fun, layered look. The butterfly graphic on the baby tee will add a cute touch to the overall outfit.
2. **Mix-and-Match**: Pair the "Y2K Baby Tee — Butterfly Print" with some neutral-colored bottoms, like the "Vintage Levi's 501 Jeans — Medium Wash" (available in our shop), to create a cute and casual outfit. You could also swap the jeans for a flowy skirt to add a more feminine touch.
3. **Bohemian Chic**: Combine the "Tie-Dye Long Sleeve — Pastel" with the "Y2K Baby Tee — Butterfly Print" and add some distressed denim or a flowy maxi skirt to create a bohemian-inspired look.

To complement these outfits, you might consider adding some statement accessories, like layered necklaces or a floppy hat, to enhance the overall aesthetic.

If you're interested in adding some new pieces to your wardrobe to further enhance these looks, I can suggest some items from our available clothing. For example, the "Vintage Levi's 501 Jeans — Medium Wash" would be a great pairing with either of the tops.

What do you think of these outfit suggestions? Would you like me to recommend more items or provide styling advice for specific occasions?

Fit card: None

Data saved: False