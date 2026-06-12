from groq import Groq
from config import Config
import ollama 
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

        
    def generate_stylist_assistant(self, prompt:str='', new_outfit:dict={}):
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
            {load_wardrobe_schema()['empty_wardrobe']['items']}
            
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
                
    
    def __str__(self):
        return f"{self.llm_model}"

if __name__ == "__main__":
    bot = Chatbot()
    