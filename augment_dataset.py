"""
Dataset Augmentation for MindMate V3
- Injects 482 failure phrases with correct labels
- Adds 5th class "chitchat" (label=4)
- Generates synonym-based augmented data
- Outputs AUGMENTED_dataset.csv
"""
import pandas as pd
import random
import re

print("📂 Loading original dataset...")
df = pd.read_csv("UPDATEDdataset.csv")
print(f"   Original: {len(df)} rows, {df['label'].nunique()} classes")
print(f"   Distribution: {df['label'].value_counts().to_dict()}")

new_rows = []

# ==============================================================================
# 1. INJECT FAILURE PHRASES WITH CORRECT LABELS
# ==============================================================================
print("\n🔧 Injecting failure phrases...")
label_map = {"sad": 1, "critical": 2, "happy": 0, "out_of_context": 3}

try:
    failures = pd.read_csv("combined_failures.tsv", sep="\t")
    for _, row in failures.iterrows():
        text = str(row["message"]).strip()
        expected = str(row["expected_class"]).strip()
        if expected in label_map and len(text) > 2:
            new_rows.append({"text": text, "label": label_map[expected]})
    print(f"   Added {len(new_rows)} failure phrases")
except FileNotFoundError:
    print("   ⚠️  combined_failures.tsv not found, skipping")

# ==============================================================================
# 2. ADD 5TH CLASS: CHITCHAT (label=4)
# ==============================================================================
print("\n💬 Adding chitchat class (label=4)...")
chitchat_examples = [
    # Weather
    "aaj mausam kaisa hai", "how is the weather today", "barish ho rahi hai",
    "bohot garmi hai aaj", "it is very hot today", "thand bohot hai",
    "it is very cold", "mausam achha hai aaj", "nice weather today",
    "monsoon aa gaya", "dhoop nikli hai", "aandhi aa rahi hai",
    "baarish mein bheeg gaya", "umbrella laya nahi", "sunlight is nice",
    # Food
    "aaj kya khaya", "what did you eat today", "biryani kha raha hu",
    "pizza mangwata hu", "momos khaane chalein", "chai pee le",
    "maggi bana raha hu", "burger achha tha", "aaj dinner bahar",
    "tiffin mein kya hai", "canteen ka khana bekar hai",
    "mummy ne achha khana banaya", "ice cream khani hai",
    "samosa kha le", "chole bhature chahiye", "dosa khaunga",
    "pani puri khaate hain", "thanda pee le", "coffee chahiye",
    "breakfast skip kar diya", "protein shake peena chahiye",
    # Sports & Entertainment
    "ipl match dekha kya", "who won the match today",
    "cricket mein kaun jeeta", "india ki team kaisi hai",
    "world cup aa raha hai", "football dekhta hai kya",
    "messi ya ronaldo", "kohli ne century maari", "dhoni is legend",
    "kaun jeeta aaj", "match maza aa gaya", "tournament kab hai",
    "olympics mein medals", "score kya hai abhi",
    # Technology & General Knowledge
    "python sikhna hai", "best coding language kya hai",
    "what is artificial intelligence", "ai kya hota hai",
    "laptop kaunsa lu", "iphone ya android", "best phone under 20k",
    "wifi password kya hai", "internet slow hai", "app crash ho rahi hai",
    "chatgpt better hai ya tu", "google ya bing", "coding seekhni hai",
    "website banana hai", "gaming laptop chahiye",
    # Casual Conversation
    "tum kaun ho", "what is your name", "who are you",
    "kya time hua hai", "what time is it", "aaj kaunsa din hai",
    "what day is it today", "tera age kya hai", "how old are you",
    "tum robot ho ya insaan", "are you a robot or human",
    "kya kar rahe ho", "what are you doing", "bore ho raha hu",
    "kuch batao mujhe", "tell me something interesting",
    "aaj ka news kya hai", "whats happening in the world",
    "funny baat bata", "koi mazak sunao", "ek story batao",
    "tell me a poem", "shayari sunao", "poem likho",
    "capital of india kya hai", "2 plus 2 kya hota hai",
    "earth round hai ya flat", "sun kitna door hai",
    "history ka fact batao", "science experiment batao",
    # Shopping & Lifestyle
    "shopping karne jaa raha hu", "kya khareedun",
    "shoes kaunse lu", "t-shirt dikha do", "sale kab hai",
    "amazon pe offer hai", "flipkart better hai", "online shopping",
    "birthday gift kya du", "gift ideas de do",
    # Academics (neutral, not stressful)
    "kal class hai", "assignment kar raha hu", "project ka topic kya lu",
    "teacher achhe hain", "college ka time kya hai",
    "library mein padh raha hu", "notes mil gaye",
    "internship ka form bhara", "placement season kab hai",
    "fest mein participate karu kya", "club join karun",
    # Greetings & Small Talk
    "hello bhai", "hi kaise ho", "kya haal chaal", "sup bro",
    "good morning", "good night", "subah ho gayi",
    "kal milte hain", "see you later", "take care",
    "long time no see", "bahut din baad", "kahan the tum",
    "sab badhiya", "theek hai sab", "chill hai bhai",
    # Random & Misc
    "aliens exist karte hain kya", "do aliens exist",
    "favourite color kya hai", "best movie konsi hai",
    "music recommend karo", "book padhun kaunsi",
    "hogwarts mein konsa house", "avengers ya justice league",
    "summer vacation plans", "winter holidays",
    "netflix kya dekhun", "web series recommend karo",
    "tiktok ban ho gaya", "instagram reels dekhte ho",
    "youtube pe kya dekhun", "podcast sunti ho",
    "dream destination kya hai", "travel karna chahta hu",
    "bike ride pe chalein", "road trip plan karu",
    "photography achhi hai", "camera kaunsa lu",
    "painting seekhni hai", "guitar bajana hai",
    "dance class join karun", "martial arts start karun",
    "kutta paalun ya billi", "pet shop kahan hai",
    "garden mein plants lagaye", "cooking seekhni hai",
    # Hindi casual
    "kya scene hai", "sab sahi hai", "mast hai bhai",
    "chill maar le", "tension mat le", "aaram se",
    "full badhiya", "ekdum jhakaas", "first class",
    "kya bolti public", "ladki patani hai", "bhai date pe ja raha hu",
    "haircut karwana hai", "gym ja raha hu workout",
    "match lagaya kya", "dream11 team banai",
    "sutta mat piyo", "cigarette chhod de", "health ka dhyan rakh",
]

# Generate variations for chitchat
chitchat_variations = []
for ex in chitchat_examples:
    chitchat_variations.append(ex)
    # Add simple variations
    if " " in ex:
        words = ex.split()
        # Shuffle word order slightly
        if len(words) > 3:
            w2 = words.copy()
            w2[1], w2[2] = w2[2], w2[1]
            chitchat_variations.append(" ".join(w2))
        # Add "bhai" or "yar" suffix
        chitchat_variations.append(ex + " bhai")
        chitchat_variations.append(ex + " yar")

# Deduplicate
chitchat_variations = list(set(chitchat_variations))
for text in chitchat_variations:
    new_rows.append({"text": text, "label": 4})
print(f"   Added {len(chitchat_variations)} chitchat examples")

# ==============================================================================
# 3. SYNONYM-BASED AUGMENTATION FOR FAILURES
# ==============================================================================
print("\n🔄 Generating synonym augmentations...")

synonym_map = {
    "sad": ["upset", "low", "down", "gloomy", "unhappy"],
    "depressed": ["devastated", "shattered", "broken", "miserable"],
    "lonely": ["alone", "isolated", "solitary", "friendless"],
    "anxious": ["worried", "nervous", "tense", "uneasy"],
    "stressed": ["overwhelmed", "pressured", "burdened", "strained"],
    "scared": ["afraid", "frightened", "terrified", "fearful"],
    "hopeless": ["helpless", "powerless", "desperate", "lost"],
    "tired": ["exhausted", "drained", "fatigued", "burnt out"],
    "angry": ["furious", "irritated", "frustrated", "annoyed"],
    "hurt": ["wounded", "damaged", "scarred", "pained"],
    "crying": ["sobbing", "weeping", "tearing up", "breaking down"],
    "fail": ["flunk", "bomb", "mess up", "screw up"],
    "sleep": ["rest", "nap", "slumber", "doze"],
    "happy": ["glad", "cheerful", "delighted", "thrilled", "joyful"],
    "excited": ["pumped", "thrilled", "ecstatic", "hyped"],
    "love": ["adore", "cherish", "care about", "treasure"],
    "hate": ["despise", "loathe", "detest", "abhor"],
    "friend": ["buddy", "pal", "mate", "companion"],
    "family": ["parents", "relatives", "household", "folks"],
    "pressure": ["stress", "burden", "weight", "tension"],
    # Hinglish synonyms
    "udas": ["dukhi", "low", "sad"],
    "pareshan": ["tension", "worried", "stressed"],
    "akela": ["lonely", "alone", "isolated"],
    "darr": ["fear", "scared", "afraid"],
    "thak": ["tired", "exhausted", "drained"],
    "bekar": ["useless", "worthless", "pointless"],
    "khush": ["happy", "glad", "excited"],
    "dost": ["friend", "buddy", "yar"],
    "padhai": ["study", "studies", "academics"],
    "neend": ["sleep", "rest", "nap"],
    "rona": ["cry", "crying", "weep"],
    "dard": ["pain", "hurt", "ache"],
}

augmented_count = 0
for _, row in pd.DataFrame(new_rows[:len(new_rows)]).iterrows():
    text = str(row["text"]).lower()
    label = row["label"]
    if label == 4:  # Skip chitchat augmentation
        continue
    for word, synonyms in synonym_map.items():
        if word in text.split():
            for syn in random.sample(synonyms, min(2, len(synonyms))):
                aug_text = text.replace(word, syn, 1)
                if aug_text != text:
                    new_rows.append({"text": aug_text, "label": label})
                    augmented_count += 1

print(f"   Generated {augmented_count} augmented samples")

# ==============================================================================
# 4. ADD MORE SAD TRAINING DATA (common phrases model misses)
# ==============================================================================
print("\n📝 Adding more sad training data...")
extra_sad = [
    # Depression - indirect phrasing
    "nothing excites me anymore", "i dont enjoy things anymore",
    "har cheez boring lagti hai", "motivation nahi hai",
    "i think i have depression", "mujhe depression hai",
    "doctor ko dikhana chahiye", "therapy leni chahiye kya",
    "feelings express nahi ho rahi", "emotions dead hain",
    "life feels so heavy", "bohot heavy lagta hai sab",
    "everyone is happy except me", "sab log khush hain bas main nahi",
    "my brain has stopped working", "dimag kaam nahi kar raha",
    "i feel like im going crazy", "pagal ho raha hu lagta hai",
    "puri duniya mere khilaf hai", "world against me",
    # Family
    "parents fight every day", "ghar pe roz ladai hoti hai",
    "papa bohot naraz hain mujhse", "mummy samajhti nahi",
    "family expectations bohot zyada hain", "compare karte hain roz",
    "ghar mein paise ki dikkat hai", "fees ke paise nahi hain",
    "mom cries every day", "mummy roz roti hai",
    "papa ko lagta hai depression fake hai",
    "parents ka pressure bohot hai", "ghar suffocating hai",
    # Academic - indirect
    "syllabus khatam nahi ho raha", "marks bohot kam aaye",
    "placement nahi ho rahi", "sab select ho gaye main reh gaya",
    "professor ne daanta sab ke saamne", "viva mein kuch nahi bola paya",
    "coaching bohot hectic hai", "assignment pending hai",
    "library mein jagah nahi milti", "notes nahi hain",
    "college jaane ka mann nahi karta", "padhai chhodna chahta hu",
    "year loss ho jayega", "drop year lena chahiye kya",
    "career ka kuch pata nahi", "future looks dark",
    # Anxiety - body symptoms
    "my heart is racing", "dil dhadak raha hai bohot",
    "hands trembling", "haath kaanp rahe hain",
    "pet mein gadbad ho rahi hai stress se",
    "stress is affecting my stomach", "body tense rehti hai",
    "sar mein dard rehta hai", "panic attack aa rahi hai",
    "saans nahi aa rahi", "cant breathe properly",
    "bohot irritable ho gaya hu", "chhoti baaton pe gussa",
    "what if i fail", "agar fail ho gaya toh",
    "kal kya hoga pata nahi", "future ki tension hai",
    "rest karne ka time nahi milta", "multitask nahi ho pata",
    "i have become very irritable", "patience khatam ho gayi",
    "i have lost confidence in myself", "confidence nahi raha",
    # Loneliness
    "i feel so alone in this world", "duniya mein akela hu",
    "mera phone kabhi nahi bajta", "nobody calls me",
    "social media pe sab ke dost hain mere nahi",
    "fest mein koi saath nahi gaya", "roommate bhi ignore karta",
    "i eat lunch alone every day", "akele khata hu roz",
    "no partner for project", "group mein bhi akela hu",
    "i dont have good relation with dad", "papa se rishta achha nahi",
    # Relationship
    "how do i forget them", "kaise bhulu unhe",
    "pyar karna galat tha kya", "was it wrong to love",
    "their memories are everywhere", "yaadein har jagah hain",
    "will anyone ever love me", "kya koi mujhse pyar karega",
    "the relationship was toxic", "toxic relationship thi",
    "even friendships got ruined", "dosti bhi kharab ho gayi",
    # Sleep
    "sone ki koshish karta hu par nahi hota",
    "i try to sleep but cant", "3-4 ghante hi so pata hu",
    "my eyes are burning", "aankhen jal rahi hain",
    "i fall asleep at 4am", "4 baje jaake neend aati hai",
    "melatonin try karu kya", "should i try melatonin",
    "din mein susta rehta hu", "no energy throughout the day",
    "i wake up trembling at night", "raat ko kaanp ke uthta hu",
    "very difficult to wake up", "uthna mushkil hota hai",
]

for text in extra_sad:
    new_rows.append({"text": text, "label": 1})
print(f"   Added {len(extra_sad)} extra sad examples")

# ==============================================================================
# 5. ADD MORE CRITICAL TRAINING DATA
# ==============================================================================
print("\n🚨 Adding more critical training data...")
extra_critical = [
    # Abuse - indirect
    "kisi ne mujhe galat tarike se touch kiya",
    "someone touched me inappropriately", "uncle did wrong things",
    "a relative did bad things at home", "neighbor harassed me",
    "dad beats me a lot", "papa bohot maarte hain belt se",
    "i am being harassed online", "online harassment ho rahi",
    "my photos were leaked", "photos leak ho gaye mere",
    "mujhe gandi gaaliyan di jaati hain", "bad words se abuse karte",
    "i need protection", "mujhe protection chahiye",
    "i am scared to go home", "ghar jaane mein darr lagta hai",
    "auto driver touched inappropriately",
    "its not my fault but people wont believe",
    "they are powerful i am not", "woh powerful hai main nahi",
    "bad things happened to me", "mere saath bura hua",
    "teacher ne galat kiya", "teacher touched inappropriately",
    "i am scared to be alone", "akele rehne mein darr",
    # Crisis - indirect
    "jeene ki koi wajah nahi hai", "no reason to be alive",
    "ab bardasht nahi hota", "i cant endure anymore",
    "i cant take it anymore", "bohot ho gaya",
    "main apne aap ko hurt karna chahta hu",
    "death would be a relief", "maut rahat hogi",
    "give up kar diya maine", "i have given up",
    "jeena worth it nahi hai", "living is not worth it",
    "everything is futile", "sab bekar hai zindagi",
    "life is a punishment", "zindagi saza hai",
    "sab kuch chhodna chahta hu", "i want to leave everything",
    "enough is enough", "ab bas bohot ho gaya",
    "jeene ka koi matlab nahi", "no meaning to life",
]

for text in extra_critical:
    new_rows.append({"text": text, "label": 2})
print(f"   Added {len(extra_critical)} extra critical examples")

# ==============================================================================
# 6. ADD MORE HAPPY TRAINING DATA
# ==============================================================================
print("\n😊 Adding more happy training data...")
extra_happy = [
    "life is going great", "zindagi achhi chal rahi hai",
    "dost se milke bohot achha laga", "felt great meeting a friend",
    "sab kuch perfect chal raha hai", "everything is going perfect",
    "i got an internship", "internship mil gayi",
    "dad gave me a gift", "papa ne gift diya",
    "painting kar raha hu bohot relaxing hai",
    "painting is very relaxing", "music sunke mood achha ho gaya",
    "dosti bohot strong hai hamari", "our friendship is very strong",
    "sab theek ho gaya hai ab", "everything is fine now",
    "mummy ne hug kiya", "papa ne bike dilwane ka bola",
    "google mein lagi hai", "sapna poora ho gaya",
    "self made feel ho raha hai", "life is good",
    "achha lagta hai jab mehnat ka result milta hai",
    "ghar ja raha hu chutti mein", "bohot excitement hai",
    "naya hobby start kiya hai", "talent hai mujhme",
    "energy high hai", "body mein confidence aa raha hai",
    "padhai bhi achhi ja rahi hai", "friends bhi achhe hain",
    "family bhi support karti hai", "grateful feel ho raha hai",
    "manager ne praise kiya", "team mein sabse achha kaam kiya",
    "career mein positive direction hai", "sab badhiya chal raha hai",
    "first salary aayi hai", "bohot amazing feel ho raha hai",
]

for text in extra_happy:
    new_rows.append({"text": text, "label": 0})
print(f"   Added {len(extra_happy)} extra happy examples")

# ==============================================================================
# COMBINE AND SAVE
# ==============================================================================
new_df = pd.DataFrame(new_rows)
combined = pd.concat([df, new_df], ignore_index=True)
combined['text'] = combined['text'].astype(str).str.lower().str.strip()
combined = combined.drop_duplicates(subset=['text'])
combined = combined.dropna()

print(f"\n📊 Final Dataset:")
print(f"   Total: {len(combined)} rows")
label_names = {0: "Happy", 1: "Sad/Stress", 2: "Critical/Risk", 3: "Out_Of_Context", 4: "Chitchat"}
for label in sorted(combined['label'].unique()):
    count = len(combined[combined['label'] == label])
    name = label_names.get(int(label), f"Unknown({label})")
    print(f"   Class {int(label)} ({name}): {count} samples")

combined.to_csv("AUGMENTED_dataset.csv", index=False)
print(f"\n✅ Saved: AUGMENTED_dataset.csv ({len(combined)} rows)")
