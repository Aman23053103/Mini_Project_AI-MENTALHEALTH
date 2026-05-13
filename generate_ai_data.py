"""
===============================================================================
🤖 AI-POWERED TRAINING DATA GENERATOR FOR MINDMATE V4
===============================================================================
Uses the Groq API (Llama 3.3 70B) to generate diverse, high-quality
training examples for each emotion class. This dramatically improves
the model's ability to understand:
  - Varied phrasing & slang
  - Hinglish (Hindi + English) code-switching
  - Misspellings and informal text
  - Negated sentiments ("not feeling good" = sad, not happy!)
  - Edge cases the model currently misclassifies
===============================================================================
"""

import csv
import time
import os
import json

# --- GROQ API SETUP ---
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

try:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq API connected!")
except Exception as e:
    print(f"❌ Groq API error: {e}")
    print("Please install groq: pip install groq")
    exit()

# === CLASS DEFINITIONS ===
CLASSES = {
    0: {
        "name": "Happy",
        "prompt": """Generate 60 diverse student messages expressing HAPPINESS, JOY, EXCITEMENT, or POSITIVE feelings. 
Rules:
- Mix English, Hindi, and Hinglish freely
- Include misspellings and informal texting style (no caps, abbreviations)
- Vary from short ("mast din tha!") to longer expressions
- Cover: academic success, friendship joy, personal achievements, festivals, good news
- Include some that could be confusing: "finally not sad anymore", "stress is over!"
- NO negative or sad content whatsoever
Examples: "aaj bahut khush hu!", "got my results and i topped!!", "life is beautiful yaar"
Return ONLY a JSON array of strings, nothing else."""
    },
    1: {
        "name": "Sad/Stress",
        "prompt": """Generate 80 diverse student messages expressing SADNESS, STRESS, ANXIETY, or DISTRESS.
Rules:
- Mix English, Hindi, and Hinglish freely 
- Include misspellings and informal texting style
- CRITICAL: Include NEGATED POSITIVE phrases that mean SAD:
  "not feeling good", "not okay", "not fine", "not happy", "can't feel good",
  "don't feel happy", "nothing feels good", "achha nahi lag raha"
- Cover: exam stress, loneliness, relationship issues, family problems, sleep issues, feeling lost
- Include indirect expressions: "kuch samajh nahi aa raha", "sab boring hai"
- Vary intensity from mild sadness to deep distress (but NOT suicidal)
Examples: "im not feeling good at all", "bahut akela feel ho raha hai", "nothing makes me happy anymore"
Return ONLY a JSON array of strings, nothing else."""
    },
    2: {
        "name": "Critical",
        "prompt": """Generate 50 diverse student messages expressing CRISIS, SUICIDAL THOUGHTS, SELF-HARM, or ABUSE situations.
Rules:
- Mix English, Hindi, and Hinglish freely
- Include misspellings and indirect expressions
- Cover: suicidal ideation, self-harm mentions, abuse situations, feeling of wanting to die
- Include euphemisms: "sab khatam karna chahta hu", "jeene ka mann nahi"
- Include negated survival: "not wanting to live", "can't go on anymore"
- These must be clearly crisis-level, not just regular sadness
Examples: "mujhe lagta hai marna better hoga", "i dont want to be here anymore", "nobody would miss me"
Return ONLY a JSON array of strings, nothing else."""
    },
    3: {
        "name": "Out_Of_Context", 
        "prompt": """Generate 50 diverse student messages that are completely OFF-TOPIC or RANDOM.
Rules:
- Mix English, Hindi, and Hinglish freely
- These should NOT relate to emotions, mental health, or feelings
- Cover: weather, food, tech, sports, general knowledge, random facts
- Include questions about the AI itself: "tum robot ho?", "who made you?"
- Include coding/tech: "python sikhna hai", "which laptop should I buy?"
Examples: "aaj mausam kaisa hai?", "pizza ya burger?", "tell me about IPL", "2+2 kitna hota hai?"
Return ONLY a JSON array of strings, nothing else."""
    },
    4: {
        "name": "Chitchat",
        "prompt": """Generate 50 diverse student CASUAL GREETING/CHITCHAT messages.
Rules:
- Mix English, Hindi, and Hinglish freely
- Cover: greetings (hi, hello, kya haal, kaise ho), small talk, casual conversation starters
- Include: "aur bata", "kya chal raha hai", "bore ho raha hu (casual, not depressed)"
- These are light, friendly, and conversational — NOT emotional
- Include some that could be confused: "how are you?" (this is chitchat, not sadness)
Examples: "hey!", "kaise ho bhai?", "kya scene hai aaj?", "good morning!"
Return ONLY a JSON array of strings, nothing else."""
    }
}

# === GENERATE DATA ===
OUTPUT_FILE = "AI_GENERATED_dataset.csv"
all_data = []

print(f"\n🤖 Generating AI-powered training data using {GROQ_MODEL}...\n")

for label, info in CLASSES.items():
    print(f"📝 Generating class {label} ({info['name']})...")
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data generator. You output ONLY valid JSON arrays of strings. No explanations, no markdown, no extra text."
                },
                {
                    "role": "user",
                    "content": info["prompt"]
                }
            ],
            max_tokens=4000,
            temperature=0.9,  # High creativity for diversity
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean up any markdown formatting
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        examples = json.loads(raw)
        
        for text in examples:
            text = str(text).strip()
            if text and len(text) > 2:
                all_data.append({"text": text, "label": label})
        
        print(f"   ✅ Generated {len(examples)} examples for {info['name']}")
        
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON parse error for {info['name']}: {e}")
        print(f"   Raw output: {raw[:200]}...")
    except Exception as e:
        print(f"   ❌ Error generating {info['name']}: {e}")
    
    time.sleep(2)  # Rate limit

# === SAVE TO CSV ===
print(f"\n💾 Saving {len(all_data)} AI-generated examples to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['text', 'label'])
    writer.writeheader()
    writer.writerows(all_data)

print(f"✅ Done! Generated {len(all_data)} new training examples.")
print(f"\nDistribution:")
from collections import Counter
counts = Counter(d['label'] for d in all_data)
for label in sorted(counts.keys()):
    print(f"   Class {label} ({CLASSES[label]['name']}): {counts[label]} examples")

print(f"\n🎯 Next step: Run train_model_v4.py to retrain with this + original data + GloVe embeddings!")
