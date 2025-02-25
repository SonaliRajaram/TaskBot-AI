from fuzzywuzzy import process
from config import service_list, intent_keywords

class Chatbot:
    def __init__(self):
        self.service_list = service_list
        self.intent_keywords = intent_keywords

    def correct_service_name(self,user_input):
        """Finds the closest matching service name."""
        user_input = user_input.lower().strip()
        normalized_services = [s.lower() for s in service_list]
    
        best_match, score = process.extractOne(user_input, normalized_services)
    
        # If the score is high enough, return the original service name
        if score > 70:
            return service_list[normalized_services.index(best_match)]
        return None

    def correct_intent(self,user_input):
        """Finds the closest matching intent from predefined keywords."""
        user_input = user_input.lower().strip()
        all_keywords = [keyword for intent in intent_keywords.values() for keyword in intent]
        best_match, score = process.extractOne(user_input, all_keywords)
    
        if score > 70:
            for intent, keywords in intent_keywords.items():
                if best_match in keywords:
                    # Check if the intent is explicitly mentioned in the user input
                    if any(keyword in user_input for keyword in keywords):
                        return intent
        return None
