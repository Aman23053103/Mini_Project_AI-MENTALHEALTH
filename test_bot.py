"""
===============================================================================
🎓 MINDMATE AI V4: STUDENT COMPANION
===============================================================================
Architecture:
  1. Attention-Enhanced Bi-LSTM for 5-class classification
  2. Confidence-based Risk Analysis (no blind keyword matching)
  3. Dynamic Response Selection from responses.json
  4. Conversational Memory (sliding window of last 5 turns)
  5. Groq API (Llama 3.3 70B) for smart fallback + response enhancement
===============================================================================
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import pickle
import json
import random
import re
import datetime
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Layer

# ==============================================================================
# 🧠 CUSTOM ATTENTION LAYER (Needed to load the model)
# ==============================================================================
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
    def build(self, input_shape):
        self.W = self.add_weight(name='attention_weight', shape=(input_shape[-1], 1), initializer='glorot_uniform', trainable=True)
        self.b = self.add_weight(name='attention_bias', shape=(input_shape[1], 1), initializer='zeros', trainable=True)
        super(AttentionLayer, self).build(input_shape)
    def call(self, x):
        e = tf.keras.backend.tanh(tf.keras.backend.dot(x, self.W) + self.b)
        a = tf.keras.backend.softmax(e, axis=1)
        output = x * a
        return tf.keras.backend.sum(output, axis=1)

# ==============================================================================
# 🔑 GROQ API (SMART FALLBACK + RESPONSE ENHANCER)
# ==============================================================================
GROQ_API_KEY = "your-api-key"  # Replace with your actual Groq API key
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast, smart, free tier
API_ACTIVE = False
groq_client = None

try:
    from groq import Groq
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        # Quick connectivity test
        test_resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        API_ACTIVE = True
        print(f"✅ Groq API Connected: {GROQ_MODEL}")
except Exception as e:
    print(f"⚠️ Groq API not available: {e}")
    API_ACTIVE = False

# ==============================================================================
# 📂 LOAD MODEL, TOKENIZER, CONFIG, AND RESPONSES
# ==============================================================================
print("🌱 Initializing MindMate AI V4... (Please wait)")

try:
    model = tf.keras.models.load_model('mental_health_model.h5', custom_objects={'AttentionLayer': AttentionLayer})
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    with open('model_config.pickle', 'rb') as handle:
        config = pickle.load(handle)
    with open('responses.json', 'r', encoding='utf-8') as f:
        RESPONSES = json.load(f)
    print("✅ All systems loaded successfully!")
except Exception as e:
    print(f"❌ Critical Error: {e}")
    exit()

MAX_LENGTH = config['max_length']
LABEL_MAP = {0: "happy", 1: "sad", 2: "critical", 3: "out_of_context", 4: "chitchat"}

# ==============================================================================
# 🧠 CONVERSATION MEMORY (Sliding Window)
# ==============================================================================
conversation_history = []  # List of {"user": str, "bot": str, "emotion": str, "risk": str}
MAX_HISTORY = 5

session_state = {
    "patient_name": "",
    "current_context": "general",       # Detected sub-topic (abuse, grief, sleep, etc.)
    "current_entertainment": None,       # Track if showing songs/movies/jokes
    "step": None,                        # Track multi-turn flow position
    "risk_trend": [],                    # Last N risk labels for trend analysis
}

# ==============================================================================
# 🔤 TEXT CLEANING & NORMALIZATION
# ==============================================================================
def clean_text(text):
    """Normalize slang and Hinglish to standard tokens."""
    text = str(text).lower().strip()
    
    slang_map = {
        # Grief
        "passed away": "grief", "died": "grief", "death": "grief",
        "mar gaye": "grief", "gone forever": "grief", "nahi rahe": "grief",
        "guzar gaye": "grief", "chale gaye": "grief", "kho diya": "grief",
        
        # Abuse & Safety (with misspelling coverage)
        "molest": "abuse", "molestation": "abuse", "gandi harkat": "abuse",
        "zabardasti": "abuse", "bad touch": "abuse", "rape": "abuse",
        "bully": "abuse", "ragging": "abuse", "eve teasing": "abuse",
        "mollest": "abuse", "mollestation": "abuse", "mollest": "abuse",
        "galat kaam": "abuse", "galat kam": "abuse", "galat harkat": "abuse",
        "gandi nazar": "abuse", "chheda": "abuse", "chhedna": "abuse",
        "gandi cheez": "abuse", "sexual harassment": "abuse",
        "safe nahi": "unsafe", "not safe": "unsafe",
        
        # Distress signals (expanded)
        "pareshan": "stressed", "parishan": "stressed", "tension": "stressed",
        "confused": "stressed", "samaj nahi": "stressed",
        "samajh nahi": "stressed", "samjh nahi": "stressed",
        "tang aa gaya": "stressed", "tang aa gayi": "stressed",
        "tang agaya": "stressed", "thak gaya": "exhausted",
        "thak gayi": "exhausted", "thak chuka": "exhausted",
        
        # Emotional numbness / apathy
        "man nahi lagta": "numb depressed", "mann nahi lagta": "numb depressed",
        "man nahi lag raha": "numb depressed", "mann nahi lag raha": "numb depressed",
        "kuch achha nahi": "sad depressed", "kuch accha nahi": "sad depressed",
        "achha nahi": "sad", "accha nahi": "sad", "acha nahi": "sad",
        "achha feel nahi": "sad", "accha feel nahi": "sad",
        "kisi bhi chiz": "nothing matters",
        "koi fayda nahi": "hopeless", "fayda nahi": "hopeless",
        "sab bekar": "hopeless", "sab same": "hopeless",
        "empty feel": "empty numb", "hollow feel": "empty numb",
        
        # Positive indicators  
        "bahtar": "better", "behtar": "better", "theek": "okay",
        "mast": "happy", "badhiya": "happy", "khush": "happy",
        
        # Context keywords
        "breakup": "heartbroken", "dhoka": "heartbroken",
        "neend nahi": "insomnia", "insomnia": "insomnia",
        "sleep nahi": "insomnia", "so nahi pata": "insomnia",
        "exam": "academic", "padhai": "academic", "study": "academic",
        "fail": "academic", "marks": "academic", "syllabus": "academic",
        "result": "academic", "cgpa": "academic", "semester": "academic",
        
        # Family context
        "papa": "family", "mummy": "family", "parents": "family",
        "ghar pe": "family", "gharwale": "family",
        
        # Requests (expanded)
        "solution": "help_request", "kya karu": "help_request",
        "kiya karu": "help_request", "ab kya karu": "help_request",
        "upay": "help_request", "tips": "help_request",
        "suggest": "help_request", "suggestions": "help_request",
        "batao": "help_request", "help": "help_request",
        "overcome": "help_request", "kaise niklu": "help_request",
        
        # Entertainment requests (expanded)
        "song": "music_request", "gana": "music_request",
        "gaana": "music_request", "music": "music_request",
        "gana suna": "music_request", "song suna": "music_request",
        "joke": "joke_request", "jokes": "joke_request",
        "mazak": "joke_request", "funny": "joke_request",
        "movie": "movie_request", "film": "movie_request",
        "movie suggest": "movie_request",
        "helpline": "helpline_request",
        
        # Acknowledgements
        "thankyou": "gratitude", "thanks": "gratitude", "shukriya": "gratitude",
        "thank you": "gratitude", "dhanyawad": "gratitude",
        "rehne do": "rejection", "chodo": "rejection", "nahi chahiye": "rejection",
        "chhodo": "rejection", "mat batao": "rejection",
        "haan": "yes", "han": "yes", "yup": "yes", "ji": "yes",
        "bilkul": "yes", "zaroor": "yes",
        "nahi": "no", "nope": "no", "mat": "no",
        
        # Suicidal language normalization (catches misspellings)
        "sucide": "suicide", "suside": "suicide", "suicid": "suicide",
    }
    
    # Sort by length (longest first) to avoid partial matches
    sorted_slang = sorted(slang_map.items(), key=lambda x: len(x[0]), reverse=True)
    
    for slang, replacement in sorted_slang:
        # Use word boundary match, but also try simple contains for multi-word
        pattern = r'\b' + re.escape(slang) + r'\b'
        text = re.sub(pattern, replacement, text)
    
    return text

# ==============================================================================
# 🎯 CONTEXT DETECTOR (Sub-topic within an emotion)
# ==============================================================================
def detect_context(text, original_text=""):
    """Detect the specific topic/context of the conversation.
    Checks both cleaned text AND original text to catch misspellings."""
    combined = text + " " + original_text.lower()
    
    # ===== GRATITUDE / FAREWELL — check FIRST so they override emotion =====
    gratitude_words = [
        "thank", "thanks", "thanku", "thankyou", "thank you", "thnx", "thnks",
        "shukriya", "dhanyawad", "dhanyavaad", "grateful", "gratitude",
        "sun ne ke liye", "sunne ke liye", "baat kar ke achha laga",
        "accha laga baat", "better feel ho raha", "better feel", "theek hu ab",
        "achha lagta hai", "help ke liye", "support ke liye",
    ]
    farewell_words = [
        "bye", "byee", "goodbye", "good bye", "tata", "alvida", "see you",
        "chalo phir", "milte hai", "milte hain", "good night", "gn",
        "chal main chalta", "ab chalta hu", "chalo bye", "ok bye",
    ]
    if any(w in combined for w in gratitude_words):
        return "gratitude"
    if any(w in combined for w in farewell_words):
        return "gratitude"  # Treat farewell same as gratitude for response routing
    
    # Abuse — check broadly (includes misspellings in original)
    abuse_words = ["abuse", "molest", "zabardasti", "unsafe", "rape", "bully", "ragging",
                   "galat kaam", "galat kam", "galat harkat", "gandi harkat", "gandi nazar",
                   "chheda", "mollest", "mollestation", "molestation", "sexual",
                   "bad touch", "eve teasing", "gandi cheez"]
    if any(w in combined for w in abuse_words):
        return "abuse"
    
    if any(w in combined for w in ["grief", "mar gaye", "death", "nahi rahe", "guzar gaye", "kho diya"]):
        return "grief"
    
    # Entertainment — check BEFORE emotional contexts to prioritize requests
    if any(w in combined for w in ["music_request", "music", "gana", "gaana", "song"]):
        return "music"
    if any(w in combined for w in ["joke_request", "joke", "jokes", "mazak", "funny bata"]):
        return "joke"
    if any(w in combined for w in ["movie_request", "movie", "film", "movie suggest"]):
        return "movie"
    
    # Academic
    if any(w in combined for w in ["academic", "exam", "padhai", "fail", "marks", "syllabus", "result", "cgpa", "semester", "backlog", "attendance", "assignment", "project", "viva"]):
        return "academic"
    # Sleep
    if any(w in combined for w in ["insomnia", "neend", "sleep", "so nahi", "uthna", "bed se"]):
        return "sleep"
    # Relationship
    if any(w in combined for w in ["heartbroken", "breakup", "dhoka", "ex ", "relationship", "crush"]):
        return "relationship"
    # Loneliness
    if any(w in combined for w in ["akela", "lonely", "alone", "koi nahi", "koi samajhta nahi", "outsider", "ignore", "dost nahi"]):
        return "loneliness"
    # Family
    if any(w in combined for w in ["papa", "mummy", "parents", "ghar wale", "family", "gharwale", "maa", "baap", "pita", "mata"]):
        return "family"
    # Stress
    if any(w in combined for w in ["stress", "stressed", "pressure", "tension", "pareshan", "pagal", "overwhelm"]):
        return "stress"
    # Motivation
    if any(w in combined for w in ["mann nahi", "motivation", "kuch karne ka mann", "energy nahi", "lazy", "procrastin"]):
        return "motivation"
    # Procrastination
    if any(w in combined for w in ["procrastination", "kal pe daal", "postpone", "baad mein", "time waste"]):
        return "procrastination"
    # Peer pressure
    if any(w in combined for w in ["peer pressure", "comparison", "log kya kahenge", "dusre sab", "behind"]):
        return "peer_pressure"
    # Body image
    if any(w in combined for w in ["body image", "mota", "patla", "weight", "ugly", "looks", "shakal"]):
        return "body_image"
    
    if any(w in combined for w in ["helpline_request", "helpline"]):
        return "helpline"
    if any(w in combined for w in ["help_request", "kya karu", "kiya karu", "ab kya", "overcome", "kaise niklu"]):
        return "help"
    if any(w in combined for w in ["rejection", "rehne do", "chodo", "chhodo"]):
        return "rejection"
    
    return "general"

# ==============================================================================
# 🔍 CLASSIFY WITH CONFIDENCE
# ==============================================================================
def classify_input(text, original_text=""):
    """
    Run the cleaned text through the Bi-LSTM model.
    Includes a keyword safety override to correct obvious misclassifications.
    Also checks original (uncleaned) text to catch misspellings.
    Returns: (predicted_class_name, confidence_score, all_probabilities)
    """
    # V3: Prevent CRITICAL condition loops by NOT prepending raw user history.
    # Passing prior toxic/critical keywords caused the model to lock into CRITICAL.
    context_prefix = ""
    # if conversation_history:
    #     recent = conversation_history[-2:]  # Last 2 turns
    #     context_parts = [h["user"] for h in recent if "user" in h]
    #     if context_parts:
    #         context_prefix = " ".join(context_parts) + " "
    
    context_text = context_prefix + text
    seq = tokenizer.texts_to_sequences([context_text])
    padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding='post')
    probabilities = model.predict(padded, verbose=0)[0]
    
    predicted_class = int(np.argmax(probabilities))
    confidence = float(np.max(probabilities))
    emotion = LABEL_MAP.get(predicted_class, "out_of_context")
    original_lower_text = original_text.lower().strip() if original_text else ""
    
    # === KEYWORD SAFETY OVERRIDE ===
    # The model frequently misclassifies. We use extensive keyword lists
    # to override: happy FIRST (protect positive), then critical, then sad.
    
    happy_keywords = [
        # Direct positive emotions
        "khush", "khushi", "happy", "excited", "amazing", "wonderful",
        "fantastic", "great day", "awesome", "celebrate", "celebration",
        "proud", "achieved", "achievement", "success", "successful",
        "won", "winner", "victory", "jeet", "jeeta", "jeeti",
        # Positive events
        "achha din", "best day", "maza aaya", "mazaa aa raha",
        "mazedaar", "mast din", "party", "festival", "masti",
        "achhe marks", "good marks", "top", "topper", "first rank",
        "placement ho gayi", "got placed", "promotion", "internship mil",
        "got internship", "selected", "scholarship mili",
        "crush said yes", "haan bol diya", "propose accept",
        # Positive states
        "confident", "confidence badh", "positive feel",
        "feeling good", "feel good", "achha feel", "accha feel",
        "achha lag raha", "accha lag raha", "badhiya", "shandaar",
        "relief", "relax", "relaxing", "peaceful", "peace",
        "better feel", "behtar", "bahtar", "improve",
        # Fun & enjoyment
        "trip", "travel", "vacation", "picnic", "outing",
        "movie dekhi", "fun movie", "gaming", "bike ride",
        "gift mila", "gift diya", "surprise", "treat",
        "tasty", "delicious", "yummy", "khaana kha",
        "prize jeeta", "trophy", "medal", "certificate",
        "appreciate", "praised", "well done", "proud hain",
        "first salary", "new phone", "new bike", "new car",
        "hobby start", "loving it", "enjoy", "enjoying",
        "dost bane", "new friends", "sunset", "nature",
        "gym", "workout", "exercise", "fit feel",
        "record banaya", "new record", "personal best",
    ]
    
    critical_keywords = [
        # English - Direct suicidal
        "die", "kill", "suicide", "suicid", "sucide", "end it", "quit life",
        "jump off", "hurt myself", "cut myself", "hang myself",
        "disappear forever", "never wake up", "end my life",
        "kill myself", "wanna die", "want to die", "better off dead",
        "no reason to live", "not worth living",
        # English - Euphemisms (indirect suicidal)
        "sleep forever", "won't be around", "not be here",
        "leave this world", "can't go on", "no point in living",
        "don't want to exist", "end everything", "final goodbye",
        "not gonna make it", "world without me", "cease to exist",
        "permanent solution", "give up on life", "life is over",
        "done with everything", "can't take it anymore",
        "end myself", "better off without me",
        "won't miss me", "nobody would miss", "nobody would notice",
        "nobody cares about me",
        # Crisis - indirect
        "took pills", "goliyan kha", "kata hai", "cut myself",
        "pills kha li", "overdose", "slit", "razor",
        "goodbye cruel", "last time we talk", "aakhri baar",
        "after tonight", "aaj raat ke baad",
        "nobody can stop me", "koi rok nahi", "mujhe koi rok",
        "i was never born", "paida na hua hota", "wish i was never born",
        "would miss me", "farak nahi padega",
        "last day", "aakhri din",
        "better if i was dead", "mera marna", "mar jana better", "dying is better",
        "world is better without me", "duniya mere bina behtar",
        "life is punishment", "zindagi saza", "zindagi ek saza",
        "cant survive another day", "ek aur din nahi",
        "cant live anymore", "nahi jee sakta aur", "cannot live anymore",
        "should take poison", "zeher kha", "zahar kha",
        "fed up with life", "tang aa gaya life",
        "given up on life", "give up on life",
        "not afraid of death", "maut se darr nahi",
        "want to leave everything", "sab chhodna", "sab chhod",
        "drink poison", "will drink poison",
        "jump in the river", "nadi mein kud",
        "cant endure", "nahi jhela jata", "jhela nahi jata",
        "no meaning to life", "jeene ka matlab nahi",
        "living is pointless", "jina bekar",
        "i will be finished", "main khatam",
        "gayab ho jana", "disappear",
        # Abuse & Safety - CRITICAL
        "molest", "molestation", "mollest", "mollestation",
        "rape", "raped", "forced", "zabardasti",
        "sexual harassment", "sexually abused", "sexual abuse",
        "bad touch", "galat touch", "galat tarike se touch",
        "gandi harkat", "galat kaam kiya", "galat kam kiya",
        "domestic violence", "beaten", "maara jaata", "maarte hain",
        "photos leak", "blackmail", "threatened",
        "bully", "bullied", "bullying", "ragging",
        "eve teasing", "stalking", "peecha karta",
        "cyber bullied", "cyber bully", "online harassment",
        "not safe", "safe nahi", "protection chahiye",
        "without my consent", "marzi ke bina",
        "cant tell anyone", "bata nahi sakti", "bata nahi sakta",
        "ashamed to tell", "sharam aati",
        "daraya dhamkaya", "dhamki",
        "galat harkat", "gandi nazar", "chheda", "chhedna",
        "galat cheez", "gandi cheez",
        "teacher ne galat", "teacher touched",
        "relative ne gandi", "chacha ne galat", "mama ne",
        "padosi ne chheda", "auto wale ne",
        "school mein bully", "seniors ragging",
        "i was beaten", "maara gaya",
        "proof nahi hai", "no proof", "powerful hai main nahi",
        "log kya kahenge", "what will people say",
        "police ko batau", "tell the police",
        "help nahi karta", "nobody helps",
        # Hinglish / Hindi - suicidal
        "marna", "mar jau", "mar jana", "marr jau", "mar jaunga",
        "mar jaungi", "mar hi jau", "mar hi jata", "maut", "maut de do",
        "mar dunga", "mar dungi", "mar dena",
        "khatam karna", "khatam kar du", "khatam karun",
        "sab khatam", "sab kuch khatam",
        "zahar", "zeher",
        "jaan dena", "jaan de du", "jaan de dunga",
        "nahi jhela", "nahi jee sakta", "nahi reh sakta",
        "nahi jeena", "jee nahi sakta", "jeena nahi chahta",
        "zindagi khatam", "zindagi se tang",
        "jeene ka mann nahi", "jeena nahi", "jeena nahi hai",
        "fanda", "latkna", "latakna",
        "chhat se", "chhatt se", "upar se kud",
        "suicide note", "goodbye forever", "alvida duniya",
        "hamesha so jau", "so jau hamesha",
        "duniya chhod", "duniya se jana", "chhod ke jana",
        "alvida",
        "kabhi na uthu", "na uthu", "uth na saku",
        "jina ka koi matlab", "jeene ka matlab",
        "jina ka fayda", "jeene ka fayda",
        "wajood khatam", "cease to exist",
        "koi bachane wala nahi", "koi bacha nahi",
    ]
    
    sad_keywords = [
        # Core emotions
        "sad", "depressed", "lonely", "anxious", "stressed", "tired",
        "exhausted", "hopeless", "worthless", "empty", "crying", "cry",
        "overwhelmed", "numb", "drained", "low feel", "not okay", "not fine",
        "not good", "mood off", "pain", "struggle", "anxiety",
        "insomnia", "neend nahi", "burnout", "burnt out",
        # Hindi core emotions
        "udas", "pareshan", "parishan", "dukhi", "dukh", "thak",
        "akela", "rona", "ro raha", "ro rahi", "rona aa raha",
        "ghabrahat", "darr lagta", "darr lag raha",
        "bekar", "thakan", "thak gaya", "thak gayi",
        "bura feel", "bura lag", "kharab", "mushkil",
        # Depression phrases
        "feel broken", "i am broken", "toot gaya", "toot chuka",
        "feel like crying", "nothing makes me happy",
        "no khushi", "khushi nahi", "koi khushi nahi",
        "dont enjoy anything", "enjoy nahi",
        "feel invisible", "invisible hu",
        "i hate myself", "nafrat karta", "nafrat karti",
        "cant do anything right", "kuch nahi hota", "mujhse kuch nahi",
        "frustrated", "mind is a mess", "gadbad chal rahi",
        "going crazy", "pagal ho raha", "pagal ho rahi",
        "brain stopped", "dimag kaam nahi",
        "irritated", "mood swings", "mood keeps changing",
        "terrible day", "bura din",
        "dont know what to do", "kuch samajh nahi", "kya karu",
        "helpless", "help nahi", "no hope", "umeed nahi",
        "dark future", "future dark",
        "boring", "meaningless", "no meaning",
        "disconnected", "door hota ja raha", "khud se door",
        "cry for no reason", "bina wajah",
        "nobody understands", "samajhta nahi", "samajhti nahi",
        "nobody cares", "parwah nahi",
        "feel like a burden", "bojh hu",
        "heart feels heavy", "heavy feel", "bhari lag",
        "hurts inside", "dard ho raha", "dard andar",
        "suffocated", "gala ghut",
        "everything is ending", "sab kuch khatam sa",
        "nobody", "no one", "koi nahi",
        # Anxiety & Stress
        "panic attack", "anxiety attack",
        "hands trembling", "kaanp rahe", "trembling",
        "heart racing", "dhadak raha",
        "cant breathe", "saans nahi", "saans lena mushkil",
        "overthinking", "overthink", "soch soch ke",
        "nervous", "bechainee", "restless",
        "cant focus", "concentrate nahi", "focus nahi",
        "mind racing", "hazar cheezein",
        "scared", "afraid", "fear", "darr",
        "worst scenario", "worst case",
        "out of control", "control se bahar",
        "unbearable pressure", "handle nahi",
        "insecure",
        "scared of being judged", "judgement se darr",
        "presentation se darr", "interview se darr",
        "scared of interview", "nervous about interview",
        "perfectionism", "deadlines", "deadline",
        "workload", "overload", "too much work",
        "no time to rest", "rest nahi",
        "body feels tense", "tense",
        "stress headache", "sar dard", "headache",
        "self doubt", "bharosa nahi",
        "no peace", "chain nahi",
        "fear paralyzes", "dar ke mare",
        # Academic pressure
        "failed", "fail ho gaya", "fail ho gayi",
        "padhai", "study pressure", "exam pressure",
        "low marks", "kam marks", "marks kam",
        "cgpa gir", "cgpa drop", "backlog",
        "not studying", "padh nahi pa raha",
        "result ka darr", "scared of result",
        "papa ko kya bataunga", "mummy ko kya bataun",
        "teacher scolded", "daant diya",
        "last in class", "sabse peeche",
        "dont understand", "samajh nahi",
        "coaching hectic", "competitive exam",
        "not getting placed", "placement nahi",
        "rejected", "reject ho gaya",
        "not submitted", "pending assignment",
        "compare karte", "compared with",
        "scholarship chali", "scholarship lost",
        "cant study", "padhai nahi",
        "fear of failure", "fail hone ka darr",
        "meet expectations", "expectations puri nahi",
        "hostel padhai", "roommate disturb",
        "online classes",
        "quit studies", "padhai chhodna",
        # Loneliness & Isolation
        "no friends", "dost nahi", "koi dost nahi",
        "left me", "chhod diya",
        "nobody talks", "baat nahi karta",
        "live alone", "akele rehna",
        "miss home", "ghar ki yaad",
        "invisible to everyone",
        "alone in group", "group mein bhi akela",
        "phone never rings", "phone nahi bajta",
        "nobody wished", "wish nahi kiya",
        "sit alone", "akela baitha",
        "eat alone", "akele khata",
        "bore everyone", "bore hu sabko",
        "keep distance", "distance banate",
        "no qualities", "qualities nahi",
        "introvert isliye", "introvert hu",
        "family busy", "busy hain mere liye",
        "talk to mom", "talk to dad",
        "no good relation", "rishta achha nahi",
        "siblings apni duniya", "apni duniya",
        "no good company", "company nahi",
        "talk to myself", "khud se baat",
        "talking to walls", "deewar se baat",
        "nobody waits", "intezaar nahi",
        "feel like outsider", "outsider hu",
        "abandoned", "abandon kar diya",
        "afraid to trust", "trust nahi",
        "betray", "dhoka dete",
        "nobody loves", "pyar nahi karta",
        "nobody hugs", "hug nahi",
        "no plans", "plan nahi hota",
        "sit at home", "ghar pe baitha",
        "dont feel like going out", "bahar jaane ka mann nahi",
        "uncomfortable at social", "social gatherings",
        "people dont like me", "pasand nahi karte",
        # Relationships & Heartbreak
        "breakup", "break up", "broke up",
        "cheated on me", "dhoka diya",
        "heart broken", "heartbroken", "dil toot",
        "betrayed", "betrayal",
        "cant forget", "bhool nahi pa raha",
        "doesnt talk to me", "baat nahi karti",
        "with someone else", "kisi aur ke saath",
        "gave everything", "sab kuch de diya",
        "trust broken", "trust tod diya",
        "blocked me", "block kar diya",
        "miss them", "yaad aati hai",
        "incomplete without", "adhuri lagti",
        "cant forget", "cant move on", "move on nahi",
        "alone on valentine",
        "proposal rejected", "reject ho gaya",
        "friendzoned", "friendzone", "friend zone",
        "one sided love", "one sided",
        "was it wrong to love",
        "painful breakup",
        "crying after breakup", "rona band nahi",
        "photos dekh ke rona",
        "dont believe in love", "vishwas nahi raha",
        "toxic relationship", "toxic thi",
        "manipulated", "manipulate kiya",
        "possessive", "controlling",
        "abusive relationship",
        "second time cheated", "dusri baar dhoka",
        "wont trust anyone", "bharosa nahi hoga",
        "love is lie", "love is a lie", "pyar dhoka",
        "nights without them", "raat nahi katti",
        "songs remind", "gaano mein yaad",
        "memories everywhere", "yaadein hain",
        "dont deserve love", "deserve nahi karta",
        "will anyone love me",
        "hurt in relationship", "relationship mein hurt",
        "friendships ruined", "dosti kharab",
        "mutual friends",
        "crazy in love", "pagal ho gaya",
        # Family issues
        "fights at home", "ladai hoti hai", "jhagda",
        "strict parents", "strict hain", "bohot strict",
        "doesnt understand", "samajhti nahi", "samajhte nahi",
        "no support", "support nahi",
        "hit me", "maara", "dad hit", "papa ne maara",
        "scolds me", "daanti", "daantii", "roz daant",
        "compared with", "comparison", "compare karte",
        "drama kar raha", "drama karti",
        "nobody listens", "sunne wala koi nahi",
        "dads anger", "papa ka gussa",
        "no love in family", "pyar nahi hai family",
        "toxic home", "ghar toxic",
        "divorce", "parents divorce",
        "dad doesnt come", "ghar nahi aate",
        "mom cries", "mummy roti hai",
        "marriage pressure", "shaadi ka pressure",
        "high expectations", "expectations zyada",
        "run away from home", "bhaag jaana",
        "scared of dad", "papa se darr",
        "dont want to go home", "ghar jaane ka mann nahi",
        "forced decision", "thop diya",
        "no value to choices", "choice ko value nahi",
        "suffocating home", "suffocating hai ghar",
        "dad drinks", "sharaab", "alcohol",
        "financial problems", "paise ki dikkat",
        "no money for fees", "fees nahi",
        "loan stress", "loan ki tension",
        "health kharab", "hospital mein",
        # Sleep issues
        "cant sleep", "insomnia", "neend nahi",
        "awake all night", "raat bhar jaag", "jaagne lagta",
        "only sleep 3", "only sleep 4", "kam so",
        "difficult to wake", "uthne mein mushkil",
        "phone all night", "raat phone",
        "nightmares", "bure sapne",
        "keep waking up", "baar baar uth",
        "sleeping pills", "neend ki goliyan",
        "no energy", "energy nahi",
        "still tired", "thaka rehta",
        "circadian", "sleep cycle",
        "fall asleep 4am", "4 baje neend",
        "afternoon nap", "nap ruins",
        "headache sleep", "aankhen jal",
        "concentration dropped", "concentration kam",
        "coffee doesnt help",
        "overthink before sleep",
        "sleep paralysis",
        "restless sleep", "restless neend",
        "trembling at night", "kaamp ke uth",
        "cry in sleep", "neend mein rota",
        "sleeping too much", "zyada so raha",
        "so pata", "nahi so pata", "so nahi pata",
        "sone ki koshish", "try to sleep",
        "3-4 ghante", "melatonin",
        "baat karta hu neend", "susta rehta",
        "eyes burning", "aankhen jal",
        # Additional depression/sad phrases (round 2)
        "ras nahi", "ras nahi raha", "interest nahi raha",
        "kisi kaam ka nahi", "useless feel",
        "duniya khilaf", "world against me",
        "express nahi", "feelings express nahi",
        "life heavy", "heavy feel",
        "khatam sa", "ending", "everything ending",
        "negativity", "negative thoughts",
        "always happy except me", "sab khush",
        "heart broken", "dil toota", "heart is broken",
        "brain stopped", "dimag band",
        "stopped working", "kaam nahi kar",
        "same day", "same struggle", "har din same",
        "no motivation", "motivation nahi",
        "galti ho gayi", "mistake", "galat ho gaya",
        "viva", "practical", "attendance",
        "notes nahi", "i dont have notes",
        "library nahi", "no space",
        "dont know how to study",
        "year loss", "drop year", "drop lena",
        "career pata nahi", "career ka kuch pata",
        "judges by marks", "judge karte",
        "pending assignment", "assignment pending",
        "hectic", "coaching hectic",
        "studying except me", "padh rahe hain",
        "marks kam", "kam marks", "low marks",
        "saath nahi", "mere saath nahi",
        "phone kabhi nahi", "phone nahi bajta",
        "social media", "except me",
        "koi saath nahi", "saath nahi gaya",
        "ignore karta", "ignore karti",
        "good relation nahi", "rishta nahi",
        "own world", "apni duniya mein",
        "good company nahi",
        "hug nahi", "koi hug nahi",
        "raat ko jagta", "jagta rehta",
        "i thought they were mine", "woh mera tha",
        "kaise bhulu", "how do i forget",
        "pyar karna galat", "wrong to love",
        "time spend kiya", "yaad aata",
        "kisi ne nahi roka", "nobody stopped",
        "galti nahi thi", "not my fault",
        "tough without", "nights tough",
        "memories everywhere", "yaadein",
        "koi pyar karega", "anyone love me",
        "parents fight", "parents ka pressure",
        "parental pressure", 
        "depression fake", "depression is fake",
        "pyar nahi family", "family pyar nahi",
        "mummy roti", "mom cries",
        "grandparents pressure", "shaadi pressure",
        "family expectations", "expectations are too high",
        "choice value nahi", "value nahi deta",
        "paise dikkat", "paise ki dikkat", "fees paise",
    ]
    
    # Out-of-context override keywords (protect chitchat from misclassification)
    ooc_keywords = [
        "weather", "mausam", "time hua", "kya time",
        "naam kya", "your name", "who are you",
        "biryani", "pizza", "burger", "maggi", "chai",
        "ipl", "cricket score", "match kaisa",
        "phone lena", "laptop", "which phone",
        "python", "coding", "code",
        "2 plus 2", "capital of",
        "robot or human", "robot ho",
        "poem", "story", "shayari",
        "game khelna", "play a game",
        "konsa din", "what day",
        "tumhe kya pasand", "what do you like",
        "garmi", "barish", "raining", "hot today",
        "konsa phone", "phone should",
        "exam kab", "when is the exam",
        "hindi samajhte", "understand hindi",
        "ai kya", "what is ai",
        "chatgpt", "better or you",
        "netflix", "book padhun", "which book",
        "hogwarts", "avengers", "justice league",
        "kya scene", "whats up", "eat today",
        "kya kar raha", "what are you doing",
        "favourite movie", "favorite movie",
        "ek shayari", "recite", "poetry",
        "tum kitne saal", "how old are you",
        "sach bolte", "tell the truth",
        "tea", "want tea", "make maggi",
    ]
    
    text_lower = text.lower()
    # Also check the original (uncleaned) input for misspellings
    original_lower = original_lower_text if original_lower_text else text_lower
    combined_check = text_lower + " " + original_lower
    
    # V3: CONFIDENCE FALLBACK — if model is unsure (<55%), rely on keywords
    if confidence < 0.55:
        has_sad = any(kw in combined_check for kw in sad_keywords)
        has_critical = any(kw in combined_check for kw in critical_keywords)
        has_happy = any(kw in combined_check for kw in happy_keywords)
        has_ooc = any(kw in combined_check for kw in ooc_keywords)
        if has_critical:
            return "critical", 0.80, probabilities
        elif has_sad:
            return "sad", 0.75, probabilities
        elif has_happy:
            return "happy", 0.75, probabilities
        elif has_ooc:
            return "chitchat", 0.70, probabilities
    
    # STEP 0: Check OOC/Chitchat first — protect chitchat from emotional misclassification
    if emotion not in ["out_of_context", "chitchat"] and any(kw in combined_check for kw in ooc_keywords):
        # Only override to chitchat if NO sad/critical keywords are present
        has_sad = any(kw in combined_check for kw in sad_keywords)
        has_critical = any(kw in combined_check for kw in critical_keywords)
        if not has_sad and not has_critical:
            return "chitchat", 0.90, probabilities
    
    # STEP 1: Check HAPPY — protect positive inputs from being overridden
    if emotion not in ["happy"] and any(kw in combined_check for kw in happy_keywords):
        # Only override to happy if NO sad/critical keywords are present
        has_sad = any(kw in combined_check for kw in sad_keywords)
        has_critical = any(kw in combined_check for kw in critical_keywords)
        if not has_sad and not has_critical:
            return "happy", 0.90, probabilities
    
    # STEP 2: Override to CRITICAL if critical keywords found
    if emotion not in ["critical"] and any(kw in combined_check for kw in critical_keywords):
        return "critical", 0.95, probabilities
    
    # STEP 3: Override to SAD if sad keywords found but model said happy/out_of_context
    if emotion in ["happy", "out_of_context", "chitchat"] and any(kw in combined_check for kw in sad_keywords):
        return "sad", 0.85, probabilities
    
    # STEP 4 (V3): Override to CHITCHAT if chitchat keywords found but model said something else
    if emotion not in ["chitchat", "out_of_context"] and any(kw in combined_check for kw in ooc_keywords):
        has_sad = any(kw in combined_check for kw in sad_keywords)
        has_critical = any(kw in combined_check for kw in critical_keywords)
        if not has_sad and not has_critical:
            return "chitchat", 0.80, probabilities
    
    return emotion, confidence, probabilities

# ==============================================================================
# ⚠️ RISK ANALYSIS ENGINE (Confidence-Based)
# ==============================================================================
_DISTRESS_INTENSIFIERS = [
    "nahi jhela", "nahi jee", "helpless", "koi nahi", "akela", "bohot",
    "mar", "suicide", "die", "kill", "end it", "give up", "haar", "tang",
    "koi sunne", "ceiling", "bed se nahi", "skip", "weight", "neend nahi",
    "dar", "khatam", "worthless", "burden", "guilty", "pagal", "trapped"
]

def analyze_risk(emotion, confidence, context, cleaned_text):
    """
    Determine risk level based on model confidence + context + trend.
    Returns: "NORMAL", "MODERATE", "HIGH", or "CRITICAL"
    """
    # RULE 1: If model says CRITICAL with high confidence → CRITICAL
    if emotion == "critical" and confidence >= 0.7:
        return "CRITICAL"
    
    # RULE 2: If context is abuse → always CRITICAL
    if context == "abuse":
        return "CRITICAL"
    
    # RULE 3: If model says critical but low confidence → HIGH (double-check)
    if emotion == "critical" and confidence < 0.7:
        return "HIGH"
    
    # RULE 4: Trend analysis - need 5+ consecutive sad AND distress words present
    recent_emotions = [h.get("emotion", "") for h in conversation_history[-5:]]
    if len(recent_emotions) >= 5 and all(e == "sad" for e in recent_emotions):
        # Only escalate if current message has distress intensifiers
        if any(kw in cleaned_text for kw in _DISTRESS_INTENSIFIERS):
            return "HIGH"
    
    # RULE 5: If model says SAD with high confidence
    if emotion == "sad" and confidence >= 0.8:
        return "MODERATE"
    
    # RULE 6: If model says SAD with lower confidence
    if emotion == "sad":
        return "LOW"
    
    return "NORMAL"

# ==============================================================================
# 🎵 ENTERTAINMENT HANDLER
# ==============================================================================
def get_entertainment(category):
    """Return a random entertainment item."""
    key_map = {"music": "songs", "joke": "jokes", "movie": "movies"}
    key = key_map.get(category, "songs")
    items = RESPONSES["entertainment"].get(key, [])
    if items:
        item = random.choice(items)
        session_state["current_entertainment"] = category
        return f"{item}\n\n👉 **Ek aur {category} chahiye?** (Haan/Nahi)"
    return random.choice(RESPONSES["sad"]["validation"])

# ==============================================================================
# 🎙️ GROQ LLM FALLBACK (Last Resort)
# ==============================================================================
def llm_fallback(user_input, risk_level):
    """Only called when no other handler can respond. Uses Groq Llama 3.3."""
    if not API_ACTIVE or not groq_client:
        return None
    
    # Build context from conversation history
    history_text = ""
    for h in conversation_history[-3:]:
        history_text += f"User: {h['user']}\nBot: {h['bot']}\n"
    
    system_prompt = """You are 'MindMate', a supportive, empathetic student companion chatbot.
RULES:
1. Keep responses SHORT (max 2-3 sentences).
2. Use 'Hinglish' (Hindi + English mix with emojis).
3. Be empathetic, act like a caring friend. Don't be clinical.
4. NEVER suggest harmful actions.
5. If the user seems in distress, gently validate their feelings.
6. Add relevant emojis to make it warm."""
    
    user_msg = f"Risk level: {risk_level}\nRecent conversation:\n{history_text}\nUser now says: \"{user_input}\""
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=150,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except:
        return None

# ==============================================================================
# ✨ RESPONSE ENHANCER (Always personalizes responses via Groq)
# ==============================================================================
_recent_responses = []
_MAX_RECENT = 20

def enhance_response(static_response, emotion, context, user_input):
    """
    ALWAYS personalizes the static response through Groq LLM to:
    1. Reference what the user actually said
    2. Use different wording each time
    Falls back to static response if API unavailable.
    """
    global _recent_responses
    
    if API_ACTIVE and groq_client:
        try:
            # Build recent conversation context
            history_snippet = ""
            for h in conversation_history[-3:]:
                history_snippet += f"User: {h['user']}\nBot: {h['bot']}\n"
            
            rephrase_prompt = f"""You are MindMate, a caring Hinglish mental health buddy for Indian students.
REWRITE the base message below to make it feel personal and connected to the user's actual words.

RULES:
1. Keep it SHORT — max 2 sentences.
2. Reference something SPECIFIC the user said (their exact worry, situation, or feeling).
3. Use warm Hinglish (Hindi + English mix) with emojis.
4. Do NOT give advice or tips — ONLY emotional validation.
5. Do NOT repeat any of these recent bot messages: {_recent_responses[-5:] if _recent_responses else 'none'}
6. Sound like a caring college friend, not a therapist.

Base message: "{static_response}"
User's latest message: "{user_input}"
User is feeling: {emotion} | Topic: {context}
Recent conversation:
{history_snippet}

Your personalized response (Hinglish, 1-2 sentences, with emojis):"""
            
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": rephrase_prompt}],
                max_tokens=120,
                temperature=0.85,
            )
            rephrased = response.choices[0].message.content.strip()
            # Remove quotes if Groq wraps the response
            rephrased = rephrased.strip('"').strip("'").strip()
            if rephrased and 10 < len(rephrased) < 350:
                static_response = rephrased
        except:
            pass  # Fall back to static response
    
    # Track this response to prevent future repeats
    _recent_responses.append(static_response)
    if len(_recent_responses) > _MAX_RECENT:
        _recent_responses.pop(0)
    
    return static_response

# ==============================================================================
# 🧩 MAIN RESPONSE ENGINE
# ==============================================================================
def get_response(emotion, confidence, risk, context, cleaned_text, original_input):
    """
    The brain of the bot. Decides what to respond based on:
    - Model's emotion classification
    - Confidence score
    - Risk level
    - Detected context
    - Conversation history
    """
    
    # ========== PRIORITY 1: CRITICAL RISK ==========
    if risk == "CRITICAL":
        if context == "abuse" or session_state.get("current_context") == "abuse":
            if session_state["step"] == "safety_check":
                if any(w in cleaned_text for w in ["yes", "haan", "han", "bilkul"]):
                    session_state["step"] = None
                    return "Shukar hai ki tu safe hai. 💙\n" + RESPONSES["abuse"]["safety_plan"]
                elif any(w in cleaned_text for w in ["no", "nahi", "nope", "unsafe"]):
                    return RESPONSES["abuse"]["safety_plan"]
            session_state["step"] = "safety_check"
            session_state["current_context"] = "abuse"
            return random.choice(RESPONSES["abuse"]["validation"]) + "\n\n" + RESPONSES["abuse"]["safety_check"]
        
        # Critical emotional distress
        response = random.choice(RESPONSES["critical"]["immediate"])
        response += "\n\n" + RESPONSES["critical"]["helplines"]
        return response
    
    # ========== PRIORITY 2: HIGH RISK ==========
    if risk == "HIGH":
        # Check if safety plan was already shown in recent turns
        safety_already_shown = any(
            "Sharp cheezein door rakh" in h.get("bot", "") 
            for h in conversation_history[-4:]
        )
        
        if not safety_already_shown:
            # First time HIGH — show safety plan
            response = random.choice(RESPONSES["critical"]["immediate"])
            response += "\n\n" + RESPONSES["critical"]["safety"]
            return response
        else:
            # Already shown safety plan — give contextual empathy instead
            validation = random.choice(RESPONSES["sad"]["validation"])
            validation = enhance_response(validation, emotion, context, original_input)
            followup = random.choice(RESPONSES["sad"]["followup"])
            return validation + "\n\n" + followup
    
    # ========== PRIORITY 3: GRIEF ==========
    if context == "grief":
        if any(w in cleaned_text for w in ["help_request", "kya karu", "kiya karu", "overcome"]):
            return RESPONSES["grief"]["advice"]
        return random.choice(RESPONSES["grief"]["validation"])
    
    # ========== PRIORITY 4: ENTERTAINMENT REQUESTS ==========
    # Check entertainment EARLY — even if model said something else
    if context in ["music", "joke", "movie"]:
        return get_entertainment(context)
    
    # Check if user wants more entertainment (broader matching)
    if session_state["current_entertainment"]:
        if any(w in cleaned_text for w in ["yes", "haan", "han", "bilkul", "aur", "ek aur", "more"]):
            return get_entertainment(session_state["current_entertainment"])
        if any(w in cleaned_text for w in ["no", "nahi", "nope", "bas", "mat", "enough"]):
            session_state["current_entertainment"] = None
            return "Theek hai! 😊 Aur kuch baat karni hai?"
    
    # ========== PRIORITY 5: HELPLINE REQUEST ==========
    if context == "helpline":
        return RESPONSES["critical"]["helplines"]
    
    # ========== PRIORITY 6: GRATITUDE / FAREWELL ==========
    if context == "gratitude" or context == "rejection":
        session_state["step"] = None
        session_state["current_entertainment"] = None
        # Always give a warm farewell — don't check emotion
        gratitude_responses = [
            "Hamesha aise hi khush raho! ✨ Take care!",
            "Glad I could help! 💙 Jab bhi baat karni ho, main yahi hu.",
            "Apna khayal rakhna bestie! 🤗 Milte hain phir!",
            "Tu brave hai yar. Take care of yourself! 💛",
            "Anytime! 😊 Remember — tu akela nahi hai. Bye!",
        ]
        return random.choice(gratitude_responses)
    
    # ========== PRIORITY 7: HELP REQUEST (User asking for advice) ==========
    if context == "help":
        # Look at the last known emotional context for advice
        last_context = session_state.get("current_context", "general")
        advice_key = last_context if last_context in RESPONSES["sad"]["advice"] else "general"
        return RESPONSES["sad"]["advice"].get(advice_key, RESPONSES["sad"]["advice"]["general"])
    
    # ========== PRIORITY 8: OUT OF CONTEXT (Model Class 3) ==========
    if emotion == "out_of_context":
        # Check if it's a greeting
        greeting_words = ["hi", "hello", "hey", "namaste", "sup", "yo", "hii", "bol", "kaise ho"]
        farewell_words = ["bye", "tata", "alvida", "see you", "chalo"]
        
        if any(w in cleaned_text.split() for w in greeting_words):
            return random.choice(RESPONSES["out_of_context"]["greeting_response"])
        if any(w in cleaned_text for w in farewell_words):
            return random.choice(RESPONSES["out_of_context"]["farewell"])
        
        # SAFETY NET: Before redirecting as OOC, check if conversation has been
        # emotional recently — if so, continue with empathy instead of redirect
        recent_emotions = [h["emotion"] for h in conversation_history[-2:]]
        if any(e in ["sad", "critical"] for e in recent_emotions):
            return random.choice(RESPONSES["sad"]["validation"]) + "\n\n" + random.choice(RESPONSES["sad"]["followup"])
        
        return random.choice(RESPONSES["out_of_context"]["redirect"])
    
    # ========== PRIORITY 9: CHITCHAT (Model Class 4 — V3 new) ==========
    if emotion == "chitchat":
        chitchat_responses = [
            "Haha interesting question! 😄 Par bata, tere dil mein kya chal raha hai?",
            "Achha topic hai! 😊 Par main toh tera support buddy hu. Kuch aur baat karni hai?",
            "Nice question bhai! 🤓 Waise tu kaisa feel kar raha hai aaj?",
            "Mast! 😄 Par yaad rakh, agar kabhi baat karni ho feelings ke baare mein, main hu!",
            "Haha yeh toh mujhse mat pooch! 😂 Par bata, sab theek hai na tere saath?",
            "Bhai yeh toh Google se pooch! 😅 Par seriously, tu theek hai na?",
            "Interesting! 🤔 Waise mera kaam toh tere mental health ka support karna hai. Bata kya scene hai?",
        ]
        return random.choice(chitchat_responses)
    
    # ========== PRIORITY 10: SAD / STRESS (Model Class 1) ==========
    if emotion == "sad":
        # Check if advice for this context was already given recently
        advice_already_given = False
        if context in ["academic", "sleep", "relationship", "loneliness", "stress", "family", "motivation"]:
            advice_already_given = any(
                context in h.get("bot", "").lower() or "Tips" in h.get("bot", "")
                for h in conversation_history[-3:]
            )
        
        # Context-specific advice (only first time for each context)
        if context in ["academic", "sleep", "relationship", "loneliness", "stress", "family", "motivation", "procrastination", "peer_pressure", "body_image"] and not advice_already_given:
            session_state["current_context"] = context
            validation = random.choice(RESPONSES["sad"]["validation"])
            validation = enhance_response(validation, emotion, context, original_input)
            advice_key = context if context in RESPONSES["sad"]["advice"] else "general"
            return validation + "\n\n" + RESPONSES["sad"]["advice"][advice_key]
        
        # Generic sad response — always enhanced with Groq for contextual connection
        session_state["current_context"] = context if context != "general" else session_state.get("current_context", "general")
        validation = random.choice(RESPONSES["sad"]["validation"])
        validation = enhance_response(validation, emotion, context, original_input)
        followup = random.choice(RESPONSES["sad"]["followup"])
        return validation + "\n\n" + followup
    
    # ========== PRIORITY 11: HAPPY (Model Class 0) ==========
    if emotion == "happy":
        happy_resp = random.choice(RESPONSES["happy"]["validation"])
        return enhance_response(happy_resp, emotion, context, original_input)
    
    # ========== FALLBACK: Gemini or Generic ==========
    llm_response = llm_fallback(original_input, risk)
    if llm_response:
        return llm_response
    
    return random.choice(RESPONSES["sad"]["validation"])

# ==============================================================================
# 📝 LOGGING
# ==============================================================================
def log_chat(patient_name, user_input, bot_reply, risk, emotion, confidence):
    """Append the conversation turn to chat_log.txt."""
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] [{patient_name}]: {user_input}\n")
        f.write(f"[{timestamp}] [MindMate] (Risk:{risk} | Emotion:{emotion} | Conf:{confidence:.0%}): {bot_reply}\n")
        f.write("-" * 40 + "\n")

# ==============================================================================
# 🚀 MAIN CHAT LOOP
# ==============================================================================
def main():
    print("\n" + "=" * 55)
    print("       🎓 MINDMATE AI V4: STUDENT COMPANION       ")
    print("=" * 55)
    
    patient_name = input("Enter Your Name: ")
    session_state["patient_name"] = patient_name
    
    # Log session start
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n{'=' * 40}\n📂 NEW SESSION (V3)\n👤 Name: {patient_name}\n🕒 Time: {start_time}\n{'=' * 40}\n")
    
    print(f"\n👋 Hello {patient_name}! Main MindMate hu — tera mental health buddy.")
    print("   Kuch bhi share kar sakta hai. (Type 'quit' to exit)\n")
    
    while True:
        try:
            user_input = input("👤 You: ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() == 'quit':
                print("\n👋 Take care! Jab bhi baat karni ho, main yahi hu. 💙")
                break
            
            # --- STEP 1: Clean ---
            cleaned = clean_text(user_input)
            
            # --- STEP 2: Classify with Model ---
            emotion, confidence, probs = classify_input(cleaned, user_input)
            
            # --- STEP 3: Detect Context ---
            context = detect_context(cleaned, user_input)
            
            # Context memory: if new context detected, update; else keep last
            if context != "general":
                session_state["current_context"] = context
            elif session_state["current_context"] in ["abuse"]:
                # Sticky context for abuse
                context = session_state["current_context"]
            
            # --- STEP 4: Risk Analysis ---
            risk = analyze_risk(emotion, confidence, context, cleaned)
            
            # Track risk trend
            session_state["risk_trend"].append(risk)
            if len(session_state["risk_trend"]) > 5:
                session_state["risk_trend"] = session_state["risk_trend"][-5:]
            
            # --- STEP 5: Generate Response ---
            bot_reply = get_response(emotion, confidence, risk, context, cleaned, user_input)
            
            # --- STEP 6: Store in Memory ---
            conversation_history.append({
                "user": user_input,
                "bot": bot_reply,
                "emotion": emotion,
                "risk": risk,
                "context": context
            })
            if len(conversation_history) > MAX_HISTORY:
                conversation_history.pop(0)
            
            # --- STEP 7: Display ---
            risk_emoji = {"NORMAL": "🟢", "LOW": "🟡", "MODERATE": "🟠", "HIGH": "🔴", "CRITICAL": "🆘"}
            print(f"\n{risk_emoji.get(risk, '⚪')} MindMate (Risk: {risk} | {emotion} {confidence:.0%}):")
            print(f"   {bot_reply}\n")
            
            # --- STEP 8: Log ---
            log_chat(patient_name, user_input, bot_reply, risk, emotion, confidence)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended. Take care! 💙")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()