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

---

### Tool 3: create_fit_card

**What it does:**
Creates a final presentation card that summarizes the recommended outfi.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
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

## Tool 5: get_saved
**What it does:**
Gets the saved favorites inside user's favorites.json

**Input parameters:**

item (str | None): The agents query for item to see if saved, if not, prompt if the user wants it saved as a favorite. If The item is None, just returns the entire favorite items/combos.

**What it returns:**
Text summary, if the an item was saved, returns "item saved".



<!-- Describe what this tool does in 1–2 sentences -->

## Planning Loop

**How does your agent decide which tool to call next?**
1. Analyze the user's request.
2. If the user is searching for clothing, call search_listings.
3. If matching items are found and wardrobe information is available, call suggest_outfit.
4. Once an outfit recommendation exists, call create_fit_card.
5. If the user requests saving an item or outfit, call save_favorite.
6.  The process ends once a fit card or final recommendation has been generated and returned to the user.

---

## State Management

**How does information from one tool get passed to the next?**
The agent stores session state in memory during the interaction.

Tracked data includes:

user search query
preferred size
budget
search results
selected item
wardrobe contents
generated outfit
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
A[User Input] --> B[Planning Loop] B --> C[search_listings] C --> D[Search Results] D --> E[suggest_outfit] E --> F[Outfit Recommendation] F --> G[create_fit_card] G --> H[Final Fit Card] H --> I[User Output] D <--> J[Session State] F <--> J C --> K[No Results] K --> I E --> L[Wardrobe Empty] L --> I G --> M[Incomplete Outfit] M --> I
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
<!-- What does the user actually see at the end? -->
