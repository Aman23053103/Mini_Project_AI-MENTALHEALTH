import re

with open('test_bot.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Make session state a dictionary of session dictionaries
code = code.replace(
    'session_state = {',
    'from collections import defaultdict\\n'
    'session_states = defaultdict(lambda: {'
)
code = code.replace(
    "    \"patient_name\": \"\",",
    "    \"patient_name\": \"User\","
)

code = code.replace('session_state[', 'session_states[session_id][')
code = code.replace('session_state.get', 'session_states[session_id].get')

# Make functions accept session_id and history where needed
code = code.replace(
    'def classify_input(text, original_text=""):',
    'def classify_input(text, original_text, history):\\n    conversation_history = history'
)
code = code.replace(
    'def analyze_risk(emotion, confidence, context, cleaned_text):',
    'def analyze_risk(emotion, confidence, context, cleaned_text, history):\\n    conversation_history = history'
)
code = code.replace(
    'def get_entertainment(category):',
    'def get_entertainment(category, session_id):'
)

# Replace function calls
code = code.replace('get_entertainment(context)', 'get_entertainment(context, session_id)')
code = code.replace(
    'get_entertainment(session_states[session_id]["current_entertainment"])',
    'get_entertainment(session_states[session_id]["current_entertainment"], session_id)'
)

code = code.replace(
    'def llm_fallback(user_input, risk_level):',
    'def llm_fallback(user_input, risk_level, history):\\n    conversation_history = history'
)

code = code.replace(
    'def enhance_response(static_response, emotion, context, user_input):',
    'def enhance_response(static_response, emotion, context, user_input, history):\\n    conversation_history = history'
)

code = code.replace(
    'def get_response(emotion, confidence, risk, context, cleaned_text, original_input):',
    'def get_response(emotion, confidence, risk, context, cleaned_text, original_input, session_id, history):\\n    conversation_history = history'
)

code = code.replace('enhance_response(validation, emotion, context, original_input)', 'enhance_response(validation, emotion, context, original_input, history)')
code = code.replace('enhance_response(happy_resp, emotion, context, original_input)', 'enhance_response(happy_resp, emotion, context, original_input, history)')

code = code.replace('llm_fallback(original_input, risk)', 'llm_fallback(original_input, risk, history)')

generate_reply_code = """
from database import save_message, get_chat_history

def generate_reply(session_id, user_message):
    history_records = get_chat_history(session_id, limit=6) # 3 user, 3 bot messages typically
    
    # Convert DB history to format expected by bot
    history = []
    curr_turn = {}
    for msg in history_records:
        if msg['sender'] == 'user':
            curr_turn['user'] = msg['message']
        elif msg['sender'] == 'bot':
            curr_turn['bot'] = msg['message']
            curr_turn['emotion'] = msg.get('emotion', 'general')
            curr_turn['risk'] = msg.get('risk_level', 'NORMAL')
            if 'user' in curr_turn:
                history.append(curr_turn)
            curr_turn = {}
            
    cleaned = clean_text(user_message)
    emotion, confidence, probs = classify_input(cleaned, user_message, history)
    context = detect_context(cleaned, user_message)
    
    if context != "general":
        session_states[session_id]["current_context"] = context
    elif session_states[session_id]["current_context"] in ["abuse"]:
        context = session_states[session_id]["current_context"]
        
    risk = analyze_risk(emotion, confidence, context, cleaned, history)
    
    session_states[session_id]["risk_trend"].append(risk)
    if len(session_states[session_id]["risk_trend"]) > 5:
        session_states[session_id]["risk_trend"] = session_states[session_id]["risk_trend"][-5:]
        
    bot_reply = get_response(emotion, confidence, risk, context, cleaned, user_message, session_id, history)
    
    # Save the interactions
    from database import save_message
    save_message(session_id, 'user', user_message)
    save_message(session_id, 'bot', bot_reply, emotion, risk)
    
    return bot_reply, emotion, risk, confidence
"""

code = code.replace('def main():', generate_reply_code + '\\n# def main():')

with open('bot_logic.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('bot_logic.py generated successfully.')
