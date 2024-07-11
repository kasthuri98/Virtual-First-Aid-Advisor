import json
import os
import datetime
from fuzzywuzzy import process  # Ensure fuzzywuzzy is installed
from report_generation import generate_first_aid_report  # Custom report generation script

# Bot name
bot_name = "Advisor"

# Global variables to track pending new entry and latest first aid interaction
pending_new_entry = None
latest_first_aid_interaction = {}
awaiting_further_treatment_response = False

# File paths
knowledge_base_path = os.path.join('C:\\Users\\Kasthuri\\PycharmProjects\\pythonProject3', 'fa.json')
conversation_log_dir = os.path.join('C:\\Users\\Kasthuri\\PycharmProjects\\pythonProject3', 'conversation_logs')

# Ensure the conversation log directory exists
os.makedirs(conversation_log_dir, exist_ok=True)

def generate_unique_filename():
    return os.path.join(conversation_log_dir, f'conversation_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt')

# Knowledge base functions
def load_knowledge_base(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"intents": []}
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError:
        return {"intents": []}

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

# Chatbot functions
def find_best_match(user_question: str, knowledge_base: dict) -> str | None:
    if "intents" not in knowledge_base:
        raise KeyError("'intents' key not found in knowledge_base")

    questions = [q["patterns"] for q in knowledge_base["intents"]]
    flat_questions = [item for sublist in questions for item in sublist]  # Flatten the list of lists
    if not flat_questions:
        return None
    best_match = process.extractOne(user_question, flat_questions)
    if best_match and best_match[1] >= 70:
        return best_match[0]
    return None

def get_responses_for_question(question: str, knowledge_base: dict) -> dict | None:
    for q in knowledge_base["intents"]:
        if question in q["patterns"]:
            return q
    return None

def store_conversation(user_input: str, bot_response: str, conversation_log: list):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_log.append({
        "timestamp": timestamp,
        "user_input": user_input,
        "bot_response": bot_response
    })

def save_conversation_log(conversation_log: list, file_name: str):
    with open(file_name, 'w') as file:
        for entry in conversation_log:
            file.write(f'{entry["timestamp"]}\n')
            file.write(f'User: {entry["user_input"]}\n')
            file.write(f'Bot: {entry["bot_response"]}\n\n')

def load_conversation_log(file_name: str) -> list:
    conversation_log = []
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for i in range(0, len(lines), 4):
                try:
                    timestamp = lines[i].strip()
                    user_input = lines[i + 1].strip().replace('User: ', '')
                    bot_response = lines[i + 2].strip().replace('Bot: ', '')
                    conversation_log.append({
                        "timestamp": timestamp,
                        "user_input": user_input,
                        "bot_response": bot_response
                    })
                except IndexError:
                    continue
    return conversation_log

def generate_firstaid_report(conversation_log, report_filename):
    latest_first_aid_interaction = None
    for entry in reversed(conversation_log):
        if "bot_response" in entry and "first aid" in entry["bot_response"].lower():
            latest_first_aid_interaction = {
                "timestamp": entry["timestamp"],
                "location": "Unknown",  # Change if location determination is implemented
                "emergency_contact": "emergency" in entry["user_input"].lower(),
                "summary": entry["user_input"],
                "first_aid_provided": entry["bot_response"]
            }
            break

    if latest_first_aid_interaction:
        generate_first_aid_report(latest_first_aid_interaction, report_filename)
    else:
        print("No first aid interactions found in conversation log.")

def initiate_emergency_contact():
  print("Bot: Contacting emergency services...")

def chat_bot(user_input, conversation_log):
    global pending_new_entry, latest_first_aid_interaction, awaiting_further_treatment_response

    knowledge_base = load_knowledge_base(knowledge_base_path)

    # Check for awaiting treatment response
    if awaiting_further_treatment_response:
        awaiting_further_treatment_response = False
        if user_input.lower() == 'yes':
            initiate_emergency_contact()
            store_conversation(user_input, "Contacting emergency services...", conversation_log)
            latest_first_aid_interaction = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": "Unknown",
                "emergency_contact": True,
                "summary": "Contacting emergency services..."
            }
            return "Contacting emergency services...", False
        else:
            return "Okay, stay safe!", False

    # Handle quit commands
    if user_input.lower() in ['quit', 'thank you', 'thanks', 'bye', 'goodbye', 'exit']:
        return "Goodbye! Stay safe.", True

    # Handle emergency contact command
    if user_input.lower() == 'emergency':
        initiate_emergency_contact()
        store_conversation(user_input, "Contacting emergency services...", conversation_log)
        latest_first_aid_interaction = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Unknown",
            "emergency_contact": True,
            "summary": "Contacting emergency services..."
        }
        return "Contacting emergency services...", False

    # Handle report generation command
    if user_input.lower() == 'report':
        report_filename = f"first_aid_report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        generate_firstaid_report(conversation_log, report_filename)
        return f"Generated first aid report: {report_filename}", False

    # Handle pending new entry
    if pending_new_entry:
        knowledge_base["intents"].append({
            "condition": pending_new_entry,
            "patterns": [pending_new_entry],
            "emergency_help": "",
            "first_aid": user_input,
            "warning": ""
        })
        save_knowledge_base(knowledge_base_path, knowledge_base)
        store_conversation(pending_new_entry, user_input, conversation_log)
        pending_new_entry = None
        return 'Thank you! The new information has been added to my knowledge base.', False

    # Check for greeting terms
    if any(word in user_input.lower() for word in ["hi", "hello", "hey"]):
        return "Hello! How can I assist you today?", False

    # Attempt to find the best match in knowledge base
    best_match = find_best_match(user_input, knowledge_base)
    if best_match:
        responses = get_responses_for_question(best_match, knowledge_base)
        if "first_aid" in responses and "emergency_help" in responses and "warning" in responses:
            response = (f'First Aid: {responses["first_aid"]}\n'
                        f'Emergency Help: {responses["emergency_help"]}\n'
                        f'Warning: {responses["warning"]}\n'
                        f'Do you need further treatment? (yes/no)')
            store_conversation(user_input, response, conversation_log)
            latest_first_aid_interaction = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": "Unknown",
                "emergency_contact": False,
                "summary": response
            }
            awaiting_further_treatment_response = True
            return response, False
        else:
            store_conversation(user_input, responses["first_aid"], conversation_log)
            latest_first_aid_interaction = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "location": "Unknown",
                "emergency_contact": False,
                "summary": responses["first_aid"]
            }
            return responses["first_aid"], False

    # Handle unrecognized input
    pending_new_entry = user_input
    return "I'm not sure how to help with that. Can you tell me more or provide the information?", False


if __name__ == '__main__':
    print("Advisor: Welcome to the Virtual First Aid Advisor!")
    conversation_log = []
    conversation_filename = generate_unique_filename()
    while True:
        user_input = input("You: ")
        response, should_exit = chat_bot(user_input, conversation_log)
        print(f"{bot_name}: {response}")
        save_conversation_log(conversation_log, conversation_filename)
        if should_exit:
            break