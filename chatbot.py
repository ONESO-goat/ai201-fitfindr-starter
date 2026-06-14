from groq import Groq
from config import Config
import ollama 
import re
import json
import gradio as gr
from utils.data_loader import load_listings, load_favorites, load_wardrobe_schema
class Chatbot:
    def __init__(self, 
                 api_key=Config.GROQ_API_KEY, 
                 llm_model:str=Config.LLM_MODEL,
                 use_ollama:bool=False) -> None:
        
        if use_ollama:
            self.backend = 'ollama'
            self.ollama_model = 'qwen3:0.6b'

            try:
                ollama.show(self.ollama_model)
                print(f"✓ Using Ollama ({self.ollama_model})")

            except Exception:
                print(f"⚠ Ollama model '{self.ollama_model}' not found")
                print(f"Run: ollama pull {self.ollama_model}")
        else:
            self.backend = "grok"
            self.ai = Groq(api_key=api_key)
        
        self.llm_model = llm_model

        
    def generate_stylist_assistant(self, wardrobe, prompt:str='', new_outfit:dict={}):
        favs = load_favorites()
        m = f"""
            \u2022The user's Favorite clothing. If there are any items seen, use that knowledge to pick out clothing that'll please the user:
                    - OUTFITS: {favs['outfits']}
                    - CLOTHING: {favs['clothing']}

        """
        
        no_question_prompt = f'''
            
            No questions were asked from the user, instead provide outfit suggestions from their wardrobe.
            
            - If the wardrobe is empty: offer general styling advice for the item bought from the user. 
            
            - If not empty: suggest specific outfit combinations using the new item
            and named pieces from the wardrobe.
            
            here is the data on the item: 
                \u2022 {self.format_dict(new_outfit)}
            
            '''
        m = [
                    {
                        "role": "system",
                        "content": (
                            """You are a helpful stylist assistant for people who are interested in fashion. 
                            These people might ask for if there are a certain clothing type or brand, best outfit combination, etc.
                            """
                            "Use only the provided outfit database to answer questions. "
                            #"Implement a script that loads the documents, cleans them, and produces chunks matching the specified chunk size and overlap. "
                            """If you couldn't find clothing that matches the person's interest; provide recommendations from the available clothing and possible outfit combos the user could enjpy.
                            You can also ask follow up questions asking for more details like size, color, or the exact brand if that wasn't provided. 
                            """
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
            Question:
            {prompt if prompt else no_question_prompt}
            
            
        
            
            The user's warbrobe. If the list/wardrobe is empty, ask questions about the user's taste and recommend clothing based on their speaking style:
            {wardrobe['items']}
            
            The user's favorite clothing and outfits:
            
                \u2022 The user's Favorite outfits:
                    - {load_favorites()["outfits"]}
            
            Available clothing inside the shop:
                {self.format_dict(load_listings()[0])}
                
            """
                    },
                ]
        if self.backend == 'grok':
            try:
                response = self.ai.chat.completions.create(
                model=self.llm_model,
                messages=m,
                
            )

                answer = response.choices[0].message.content
                
                if answer:
                
                    return answer
                print("No answer generated.")
                return ''
            
            except Exception as ex:
                print(f"There was an error while generating response: \n\t\u2022 {ex}")
                #input("\npress ENTER for knowledgement ")
                
        else:
            try:
             
                client = ollama.Client(timeout=60.0)

               
                kwargs = {
                    'model': self.ollama_model,
                    'messages': m,
                    'options': {
                        'temperature': 0.2
                    }
                }
            

                
                response = client.chat(**kwargs)

                content = response['message']['content']
                print("\nOllama Response and content are created successfully\n")
              
                #print(f'\n\n\t\u2022CONTENT: {content}')
                return content

            except Exception as e:
                print(f"⚠ Ollama generation error: {e}")

                return ""
    
    def format_dict(self, x):
        txt = "=========================================\n"
        for keys, values in x.items():
            txt += f" - The {keys} for the item: {values}\n"
        txt += "=========================================\n"
        return txt
    
    def generate_scoring(self, description:str, item:dict):
        
        m = [
                    {
                        "role": "system",
                        "content": (
                            """You are a fashion item relevance scorer.

Task:
Given a user description and an item listing, determine how well the item matches.

Output Rules:
- Return ONLY a single number.
- The number must be between 0 and 10.
- Decimals are allowed.
- Do NOT explain your answer.
- Do NOT output any text besides the number.
- Examples:
  0
  3.5
  8
  10"""
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
            The description of the item:
            {description}
            
            The item data:
                \u2022{self.format_dict(item)}
            """,
                    },
                ]
        if self.backend == 'grok':
            try:
                response = self.ai.chat.completions.create(
                model=self.llm_model,
                messages=m,
                
            )

                answer = response.choices[0].message.content
                
                
                if answer:
                    return float(answer.strip())
                print("No answer generated.")
                return ''
            
            except Exception as ex:
                print(f"There was an error while generating response: \n\t\u2022 {ex}")
                #input("\npress ENTER for knowledgement ")
                
        else:
            try:
             
                client = ollama.Client(timeout=60.0)

               
                kwargs = {
                    'model': self.ollama_model,
                    'messages': m,
                    'options': {
                        'temperature': 0.2
                    }
                }
            

                
                response = client.chat(**kwargs)

                content = response['message']['content']
                print("\nOllama Response and content are created successfully\n")
              
                #print(f'\n\n\t\u2022CONTENT: {content}')
                return content

            except Exception as e:
                print(f"⚠ Ollama generation error: {e}")

                return ""
                
    def background_helper(self, description:str, item:dict={}):
        
        if not item:
            item_txt = '''
                The user didn't provide an item for you to analyze, 
                this means youll have to search inside available listings and find clothing that match the description.
                To do this, set "search_listings" to True inside the returning dictionary
            '''
            
        else:
            item_txt = self.format_dict(item)
            
        BACKGROUND_HELPER_SYSTEM_PROMPT = """You are a fashion query parser. Your ONLY job is to return a single JSON object — no explanation, no markdown, no extra text.

## YOUR TASK
Parse the user's description and item data, then return a JSON object deciding which functions to call.


## FUNCTION REFERENCE

| Function | Purpose | Call when |
|---|---|---|
| search_listings | Find items matching description, size, max_price | User wants to find/browse items |
| suggest_outfit | Build an outfit around a specific item + wardrobe | A specific item is known |
| create_fit_card | Generate an OOTD Instagram caption | User wants to share/post the look |
| save_favorite | Save outfit or item to favorites | User expresses they want to keep/save it |

## OUTPUT SCHEMA
Return EXACTLY this shape. No extra keys. No explanation.

{
    "description": "<concise item keywords, e.g. 'vintage graphic tee'>",
    "size": "<size string or null>",
    "max_price": <number or null>,
    "search_listings": <true or false>,
    "suggest_outfit": <true or false>,
    "create_fit_card": <true or false>,
    "save_favorite": <false or "clothing" or "outfits">
}

## RULES
- save_favorite is "outfits" when the user wants a full look (event, occasion, trip)
- save_favorite is "clothing" when the user wants a single piece saved
- save_favorite is false when the user does not mention saving or liking anything
- suggest_outfit is true whenever the user mentions styling, outfits, or what to wear with it
- create_fit_card is true only when the user wants to post, share, or show off the look
- All values must be valid JSON — use null not None, true/false not True/False

## EXAMPLES

Input: "vintage graphic tee under $30 size M, I wear baggy jeans and chunky sneakers"
Output:
{
    "description": "vintage graphic tee",
    "size": "M",
    "max_price": 30,
    "search_listings": true,
    "suggest_outfit": true,
    "create_fit_card": false,
    "save_favorite": false
}

Input: "going on a summer vacation with family, need a full outfit, want to post it"
Output:
{
    "description": "summer vacation outfit",
    "size": null,
    "max_price": null,
    "search_listings": true,
    "suggest_outfit": true,
    "create_fit_card": true,
    "save_favorite": "outfits"
}

Input: "found this floral dress on Depop, is it a good deal?"
Output:
{
    "description": "floral dress",
    "size": null,
    "max_price": null,
    "search_listings": false,
    "suggest_outfit": false,
    "create_fit_card": false,
    "save_favorite": false
}
"""
        
        m = [
                    {
                        "role": "system",
                        "content": BACKGROUND_HELPER_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        
                        The description of the item:
                        {description}
                        
                        The item data:
                            \u2022{item_txt}
                        """,
                    }
                ]
        if self.backend == 'grok':
            try:
                response = self.ai.chat.completions.create(
                model=self.llm_model,
                messages=m,
                
            )

                answer = response.choices[0].message.content
                
                
                if answer:
                    return self.parse_background_helper_response(answer)
                print("No answer generated.")
                return {}
            
            except Exception as ex:
                print(f"There was an error while generating response: \n\t\u2022 {ex}")
                #input("\npress ENTER for knowledgement ")
                
        else:
            try:
             
                client = ollama.Client(timeout=60.0)

               
                kwargs = {
                    'model': self.ollama_model,
                    'messages': m,
                    'options': {
                        'temperature': 0.2
                    }
                }
            

                
                response = client.chat(**kwargs)

                content = response['message']['content']
                print("\nOllama Response and content are created successfully\n")
              
                #print(f'\n\n\t\u2022CONTENT: {content}')
                return self.parse_background_helper_response(content)

            except Exception as e:
                print(f"⚠ Ollama generation error: {e}")

                return {}
                
    def parse_background_helper_response(self, response: str) -> dict:
        """
        Parses the LLM's response from background_helper into a valid Python dict.
        Handles JSON wrapped in markdown code blocks, stray text, and common model quirks.
        """
        if not response:
            raise ValueError("LLM returned an empty or None response.")

        # 1. Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        cleaned = re.sub(r"```(?:json)?\s*", "", response).replace("```", "").strip()

        # 2. Extract the first {...} block in case the model added commentary
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in response: {response!r}")
        
        json_str = match.group(0)

        # 3. Fix unquoted None → null, True/False are already valid JSON
        #    but Python-style None needs to become null
        json_str = re.sub(r'\bNone\b', 'null', json_str)
        json_str = re.sub(r'\bTrue\b', 'true', json_str)
        json_str = re.sub(r'\bFalse\b', 'false', json_str)

        # 4. Parse
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nRaw string was: {json_str!r}")

        # 5. Validate expected keys exist
        expected_keys = {
            "max_price", "size", "description",
            "search_listings", "suggest_outfit",
            "create_fit_card", "save_favorite"
        }
        missing = expected_keys - parsed.keys()
        if missing:
            raise ValueError(f"LLM response missing expected keys: {missing}")

        # 6. Coerce types to be safe
        parsed["max_price"] = float(parsed["max_price"]) if parsed.get("max_price") else None
        parsed["size"] = str(parsed["size"]) if parsed.get("size") else None
        parsed["search_listings"] = bool(parsed.get("search_listings", False))
        parsed["suggest_outfit"] = bool(parsed.get("suggest_outfit", False))
        parsed["create_fit_card"] = bool(parsed.get("create_fit_card", False))

        # save_favorite can be False, 'clothing', or 'outfit'
        sf = parsed.get("save_favorite")
        if sf not in (False, None, "clothing", "outfit"):
            parsed["save_favorite"] = False  # safe fallback

        return parsed
    def __str__(self):
        return f"{self.llm_model}"

if __name__ == "__main__":
    bot = Chatbot()
    print(bot.background_helper("vintage graphic tee under $30 size M, I wear baggy jeans and chunky sneakers"))
    