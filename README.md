# FitFindr

## Project Overview

FitFindr is an AI-powered fashion assistant that helps users discover secondhand clothing items, generate outfit recommendations using their existing wardrobe, and create a final fit card summarizing the look. The agent uses a multi-step planning loop that connects several tools together to move from a natural language request to a complete outfit recommendation.

---

# Tool Inventory

## Tool 1: search_listings

### Purpose

Searches the clothing listings database using a user's clothing preferences, size, and budget constraints.

### Function Signature

```python
search_listings(description: str, size: str, max_price: float)
```

### Inputs

| Parameter   | Type  | Description                                           |
| ----------- | ----- | ----------------------------------------------------- |
| description | str   | Natural language description of desired clothing item |
| size        | str   | Preferred clothing size                               |
| max_price   | float | Maximum budget                                        |

### Output

Returns a list of matching clothing item dictionaries containing:

* item title
* category
* size
* price
* description
* brand
* style tags

Example:

```python
[
    {
        "title": "Vintage Band Tee",
        "size": "M",
        "price": 25.0,
        "category": "tops"
    }
]
```

---

## Tool 2: suggest_outfit

### Purpose

Generates outfit recommendations by combining a selected listing with items already stored in the user's wardrobe.

### Function Signature

```python
suggest_outfit(new_item: dict, wardrobe: dict)
```

### Inputs

| Parameter | Type | Description            |
| --------- | ---- | ---------------------- |
| new_item  | dict | Selected clothing item |
| wardrobe  | dict | User wardrobe data     |

### Output

Returns an outfit string containing:

* top
* bottom
* shoes
* accessories (optional)
* styling explanation

Example:

```text

1. Pair the Y2K Baby Tee — Butterfly Print with the Baggy straight-leg jeans, dark wash (w_001) for a casual, streetwear-inspired look. The contrast between the fitted top and the baggy jeans will create a cool, relaxed vibe.

2. Combine the Y2K Baby Tee — Butterfly Print with the Wide-leg khaki trousers (w_002) for a more bohemian, earthy look. The flowy trousers will complement the cute butterfly graphic on the top.

3. Layer the Oversized grey crewneck sweatshirt (w_004) over the Y2K Baby Tee — Butterfly Print for a cozy, oversized look. This will add a nice texture and depth to the outfit.

4. Pair the Y2K Baby Tee — Butterfly Print with the Black combat boots (w_008) and the Black crossbody bag (w_010) for a grunge-inspired look. The boots and bag will add an edgy touch to the outfit.
```

---

## Tool 3: create_fit_card

### Purpose

Creates a final presentation card summarizing the generated outfit recommendation.

### Function Signature

```python
create_fit_card(outfit: str)
```

### Inputs

| Parameter | Type | Description                                       |
| --------- | ---- | ------------------------------------------------- |
| new_item  | dict | Outfit found by search_listing                    |

### Output

Returns a string fit caption containing:

* outfit title
* clothing pieces
* style description
* estimated cost
* styling notes

Example:

```test
    Cozying up in my new Oversized Flannel Shirt — Plaid Red/Black from Woolrich, which I scored for $50 on the Woolrich website - I'm loving the grunge vibes it's giving me. Paired it with my fave Baggy straight-leg jeans, dark wash, and Black combat boots for a laid-back look that's perfect for a casual day out, and I'm feeling like a total 90s kid. The Oversized Flannel Shirt is definitely a new staple in my wardrobe, and I'm excited to mix and match it with other pieces to create the perfect streetwear-inspired look.
```

---

## Additional Tool: save_favorite

### Purpose

Allows users to save favorite items or outfit recommendations.

### Function Signature

```python
save_favorite(item_id: str, user_id: str)
```

### Output

Returns a confirmation message if saved successfully.

---

## Additional Tool: save_history

### Purpose

Stores interaction history in a JSON file.

### Function Signature

```python
save_chat_history(
    user, 
    response,
    caption, 
    outfit_suggestion,
    new_item=None, 
    was_saved=False
)
```

### Output

Returns confirmation that the session was saved.

---

# Planning Loop

The agent uses conditional logic to determine which tool should run next.

1. Analyze the user's request.
2. If the request contains clothing preferences, call `search_listings`.
3. Check search results:

   * If results exist, store them in session state.
   * If no results exist, stop the workflow and suggest broader criteria.
4. Select the best matching item.
5. Check whether wardrobe data exists:

   * If wardrobe data exists, call `suggest_outfit`.
   * If wardrobe data is empty, call `suggest_outfit` with an empty wardrobe and generate styling advice instead.
6. Store the generated outfit.
7. Call `create_fit_card`.
8. If the user requests saving:

   * Call `save_favorite`
   * Call `save_history`
9. Return the final fit card.

The agent does not blindly call every tool. It checks the results of previous tools and adapts its behavior when data is missing or no listings are found.

---

# State Management

The agent maintains a session state dictionary during each interaction.

Example:

```python
session_state = {
    "query": None,
    "search_results": [],
    "selected_item": None,
    "wardrobe": {},
    "generated_outfit": None
}
```

## Stored Information

* User query
* Preferred size
* Budget
* Search results
* Selected item
* Wardrobe contents
* Generated outfit

## Data Flow

1. `search_listings` returns matching items.
2. The selected item is stored in session state.
3. The stored item is passed directly into `suggest_outfit`.
4. `suggest_outfit` generates an outfit and stores it.
5. The stored outfit is passed directly into `create_fit_card`.

This allows information to flow between tools without requiring the user to re-enter data.

---

# Error Handling

| Tool            | Failure Mode               | Agent Response                                                    |
| --------------- | -------------------------- | ----------------------------------------------------------------- |
| search_listings | No matching results        | Inform the user and suggest changing budget, size, or description |
| suggest_outfit  | Empty wardrobe             | Generate styling recommendations using only the selected item     |
| create_fit_card | Missing outfit information | Generate a text-based summary instead                             |
| save_favorite   | Save operation fails       | Display error message and allow retry                             |
| save_history    | File save fails            | Warn user and continue interaction                                |

## Example Failure Test

### Test Input

```text
designer ballgown size XXS under $5
```

### Result

`search_listings` returned zero matches.

### Agent Response

The agent informed the user that no listings matched the request and suggested:

* increasing budget
* broadening size requirements
* using a less specific search description

The workflow stopped instead of continuing to outfit generation.

---

# Spec Reflection

## How the Spec Helped

The planning specification helped define tool interfaces before implementation. Having clear inputs, outputs, and failure behavior made it easier to build and test each tool independently before connecting them through the planning loop.

## Divergence From the Spec

The original specification assumed wardrobe information would always be available. During implementation, an additional fallback path was added to handle empty wardrobes. Instead of failing, the agent now generates styling suggestions using only the newly found item.

---

# AI Usage

## Instance 1

### AI Tool Used

Claude

### Task

Quickly generate a helper _parse fuction for returning json from the LLM inside the chatbot class.

### What I Reviewed

I read through the generated function to make sure the logic matched what I wanted and that it fit the structure of my chatbot class.

### What I Changed

Zero changes were made. I used the generated function as is because it matched the requirements and was similar to parsing code I have used in previous projects.
---

## Instance 2

### AI Tool Used

Chatgpt

### Task

Review my README.md and planning.md against the project rubric and identify missing requirements.

### What I Reviewed

I compared the feedback against the rubric and checked whether my documentation covered each required section.

### What I Changed

I updated the planning.md and README sections that were missing rubric requirements, including additional detail for the planning loop, state management, and documentation sections.
---

# Example Interaction

### User Query

> I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers.

### Step 1

Call:

```python
search_listings(
    description="vintage graphic tee",
    size="M",
    max_price=30.0
)
```

Returns:

```python
[
    {"title": "Vintage Band Tee", "price": 25}
]
```

### Step 2

Call:

```python
suggest_outfit(
    new_item=selected_item,
    wardrobe={
        "pants": ["Baggy Jeans"],
        "shoes": ["Chunky Sneakers"]
    }
)
```

Returns:

```python
{
    "shirt": "Vintage Band Tee",
    "pants": "Baggy Jeans",
    "shoes": "Chunky Sneakers",
    "accessory": "Silver Chain"
}
```

### Step 3

Call:

```python
create_fit_card(outfit)
```

Returns a completed fit card.

### Final User Output

**Vintage Streetwear Fit**

* Vintage Band Tee
* Baggy Jeans
* Chunky Sneakers
* Silver Chain

Styling Notes:

A relaxed streetwear outfit inspired by 90s fashion. The oversized graphic tee pairs naturally with baggy denim and chunky sneakers for a cohesive casual look.
