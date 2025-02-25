from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from config import service_list
from chatbot import Chatbot
from validators import extract_name, is_valid_email, extract_email, is_valid_phone, extract_phone
import pandas as pd
import traceback
import os


app = Flask(__name__)
CORS(app)

# AI Model
model = OllamaLLM(model="llama3.2:1b")

# Chatbot Prompt Template
template = """
You are a customer service chatbot for Skill Source services. Respond accurately to customer inquiries while ensuring relevance to home maintenance and repair services.

Context: {context}
User Input: {user_input}

Response:
"""
prompt = ChatPromptTemplate.from_template(template)
chatbot_pipeline = prompt | model

# Initialize Chatbot
chatbot = Chatbot()

# Store user session data
user_sessions = {}

# Core Chatbot Logic
def process_user_message(session_id, user_input):
    try:
        context = user_sessions.get(session_id, {})

        detected_intent = chatbot.correct_intent(user_input)
    
        # Greeting
        if detected_intent == "greeting":
            return "Hello! How can I assist you today?"
    
        # Service Inquiry
        if detected_intent == "service" or context.get("step") == "waiting_for_service":
            # If the user is already in the service selection step, check for a valid service
            if context.get("step") == "waiting_for_service":
                service_name = chatbot.correct_service_name(user_input)
                if service_name:
                    user_sessions[session_id] = {"service": service_name, "step": "waiting_for_name"}
                    return f"Great! You have chosen {service_name}. Please provide your name."
                else:
                    return "Sorry, we couldn't recognize the service. Please select from the list above."
            else:
                # If the user is not in the service selection step, list the services
                user_sessions[session_id] = {"step": "waiting_for_service"}
                return "We offer the following services:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(service_list)]) + ".\nWhat service do you need?"
    
        # Handling Name Input
        if context.get("step") == "waiting_for_name":
            name = extract_name(user_input)
            if name.replace(" ", "").isalpha():
                user_sessions[session_id]["name"] = name
                user_sessions[session_id]["step"] = "waiting_for_email"
                return "Thanks! Please provide your email."
            return "Invalid name. Please enter a valid name (letters only)."
    
        # Handling Email Input
        if context.get("step") == "waiting_for_email":
            email = extract_email(user_input) or user_input.strip()
            if is_valid_email(email):
                user_sessions[session_id]["email"] = email
                user_sessions[session_id]["step"] = "waiting_for_phone"
                return "Got it! Now, please enter your phone number."
            return "Invalid email format. Please enter a valid email address."
    
        # Handling Phone Input
        if context.get("step") == "waiting_for_phone":
            phone = extract_phone(user_input) or user_input.strip()

            if is_valid_phone(phone):
                user_sessions[session_id]["phone"] = phone
                user_data = user_sessions.pop(session_id)
                save_to_excel(user_data)
                return (f"Thank you {user_data['name']}! Your request for {user_data['service']} is booked.\n"
                        f"You will receive a confirmation email at {user_data['email']} and an agent will contact you on {phone} shortly for further details.")       
            return "Invalid phone number. Please enter a 10-digit number."

        # Cancel Request
        if detected_intent == "cancel":
            return "Your service cancellation request has been received. You will receive an email confirmation shortly."
    
        # Reschedule Request
        if detected_intent == "reschedule":
            return "You can reschedule your service by calling +91 9789735701."
    
        # Working Hours Inquiry
        if detected_intent == "working_hours":
            return "Our service hours are 9:00 AM - 8:00 PM on weekdays. Contact us for urgent assistance!"
    
        # Pricing Inquiry
        if detected_intent == "pricing":
            return "For pricing details, please call +91 9789735701."
    
        # Greeting Response
        if detected_intent == "thanks":
            return "You're welcome! Have a great day."
    
        # Default AI Response
        ai_response = chatbot_pipeline.invoke({"context": context, "user_input": user_input})
        return ai_response if ai_response else "I'm sorry, I didn't understand that. Could you please rephrase?"
    
    except Exception as e:
        # Log the error and send a generic error message
        print(f"Error: {e}")
        print(traceback.format_exc())
        return "An error occurred while processing your request. Please try again later."


def save_to_excel(user_data, filename="user_data.xlsx"):
    try:
        # Extract data
        data = {
            "Name": [user_data.get('name', '')],
            "Service": [user_data.get('service', '')],
            "Email": [user_data.get('email', '')],
            "Phone": [user_data.get('phone', '')]
        }

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Check if file exists
        if os.path.exists(filename):
            existing_df = pd.read_excel(filename, engine="openpyxl")  
            df = pd.concat([existing_df, df], ignore_index=True)

        # Save to Excel file
        df.to_excel(filename, index=False, engine="openpyxl")  

    except Exception as e:
        # Log the error and print traceback
        print(f"Error saving to Excel: {e}")
        print(traceback.format_exc())


# Flask API Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        session_id = data.get("session_id", "default_user")
        user_message = data.get("message", "").strip().lower()

        response = process_user_message(session_id, user_message)

        return jsonify({"response": response})
    
    except Exception as e:
        # Log the error and send a generic error message
        print(f"Error in chat route: {e}")
        print(traceback.format_exc())
        return jsonify({"response": "An error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
