



class Prompts:
    def available_items(self):
        
        
        ret =  """
        {
            'id': id, 
            'title': title, 
            'description': description, 
            'category': category, 
            'tags': style_tags (list), 
            'size': size,
            'condition': condition, 
            'price': price (float), 
            'colors': colors (list), 
            'brand': brand, 
            'platform': platform
        }
        
        """