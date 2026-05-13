"""
100 simulated student conversations across 10 mental health topics.
Each student has 10-20 turns of realistic dialogue.
Format: list of (student_id, topic, [list of messages])
"""

# TOPIC 1: DEPRESSION (10 students)
DEPRESSION_CONVOS = [
    ("S001", "depression", [
        "hi bhai", "bohot sad feel ho raha hai aaj", "kuch achha nahi lagta",
        "har din same boring zindagi", "koi samajhta nahi mujhe",
        "main apne aap se nafrat karta hu", "sab bekar hai",
        "mann nahi lagta kisi kaam mein", "kya karu bata na",
        "haan thoda better feel ho raha hai", "thanks bhai", "bye"
    ]),
    ("S002", "depression", [
        "hello", "i feel so low today", "nothing excites me anymore",
        "i feel like a burden on everyone", "i cry every night",
        "my friends dont understand", "i feel invisible",
        "nobody cares about me", "what should i do",
        "music suna de koi achha sa", "thanks", "bye"
    ]),
    ("S003", "depression", [
        "hey", "mujhe depression hai", "doctor ko dikhau kya",
        "mann nahi lagta kisi bhi cheez mein", "rona aata hai bas",
        "puri duniya mere khilaf hai", "koi umeed nahi dikhti",
        "main toot chuka hu completely", "aur kitna bardasht karu",
        "koi joke suna de", "aur ek", "bas theek hai bye"
    ]),
    ("S004", "depression", [
        "namaste", "aaj bahut bura din tha", "exam mein fail ho gaya",
        "papa bohot naraz hain", "lagta hai main kisi kaam ka nahi",
        "sab log judge karte hain", "kya fayda hai padhai ka",
        "haan", "tips de padhai ke", "try karunga", "shukriya bye"
    ]),
    ("S005", "depression", [
        "hi", "i think i have depression", "i cant enjoy anything",
        "even my hobbies feel boring", "i feel empty inside",
        "my heart feels so heavy all the time", "i lost interest in everything",
        "sometimes i just stare at the wall", "is this normal",
        "haan", "okay thanks", "bye"
    ]),
    ("S006", "depression", [
        "bhai sun na", "bohot low feel ho raha hai", "kuch bhi thik nahi hai life mein",
        "padhai nahi hoti", "dost bhi nahi hain", "family bhi samajhti nahi",
        "ek dum akela hu main", "koi baat karne wala nahi",
        "haan music sunna hai", "aur ek", "theek hai thanks"
    ]),
    ("S007", "depression", [
        "hey bhai", "feeling terrible today", "broke up with my gf last week",
        "uske baad se sab bekar lagta hai", "motivation nahi hai kuch karne ki",
        "uthne ka mann nahi hota subah", "pura din bed pe padha rehta hu",
        "khana bhi nahi khata properly", "kya karu yar",
        "haan try karunga", "thanks", "bye"
    ]),
    ("S008", "depression", [
        "hello bhai", "zindagi bohot boring ho gayi hai",
        "har din same routine", "nothing new nothing exciting",
        "mann nahi karta kuch bhi karne ka", "social media pe sab khush hain",
        "bas main hi hu sad", "kya galat hai mere saath",
        "movie suggest kar", "achhi hai", "bye thanks"
    ]),
    ("S009", "depression", [
        "hi", "mera mood bohot kharab hai aaj", "college mein kuch hua",
        "friends ne ignore kiya mujhe", "canteen mein akela tha",
        "lagta hai main boring hu sabke liye", "koi baat nahi karta",
        "i feel worthless", "koi tips de motivation ki",
        "haan", "thanks yar", "bye"
    ]),
    ("S010", "depression", [
        "hey", "bahut dard ho raha hai andar se", "kisi ko bata nahi sakta",
        "sab kehte hain strong ban", "par main strong nahi hu",
        "feelings express nahi ho rahi", "bohot heavy lagta hai sab kuch",
        "rona aata hai par ro nahi pata", "help karo please",
        "joke suna de thoda", "haha achha tha", "bye bhai"
    ]),
]

# TOPIC 2: ANXIETY & STRESS (10 students)
ANXIETY_CONVOS = [
    ("S011", "anxiety", [
        "hi", "bohot stressed hu yar", "exam kal hai aur kuch nahi padha",
        "panic ho raha hai", "kya karu ab last minute mein",
        "neend nahi aa rahi tension se", "haath kaanp rahe hain",
        "deep breath lena chahiye kya", "haan", "thanks bhai", "bye"
    ]),
    ("S012", "anxiety", [
        "hello", "i am having a panic attack", "my heart is beating so fast",
        "i cant breathe properly", "everything feels out of control",
        "i feel like something bad will happen", "please help me calm down",
        "haan", "okay trying deep breathing", "feeling a bit better", "thanks"
    ]),
    ("S013", "anxiety", [
        "hey bhai", "interview hai aaj bohot nervous hu",
        "agar reject ho gaya toh", "sab kuch kharab ho jayega",
        "overthinking ho rahi hai", "pet mein gadbad ho rahi hai",
        "kaise control karu anxiety", "haan", "try karunga", "thanks", "bye"
    ]),
    ("S014", "anxiety", [
        "hi", "presentation deni hai class mein", "bohot darr lag raha hai",
        "agar galti ho gayi toh sab hasenge", "stage fright hai bohot",
        "haath paer kaanp rahe hain", "koi tips de na",
        "haan", "deep breath le raha hu", "better lag raha hai", "thanks"
    ]),
    ("S015", "anxiety", [
        "namaste", "future ke baare mein bohot tension hai",
        "kya hoga graduation ke baad", "placement nahi ho rahi",
        "ghar waale pooch rahe hain", "pressure bohot hai",
        "kal kya hoga pata nahi", "darr lagta hai",
        "koi music suna do", "achha hai", "bye"
    ]),
    ("S016", "anxiety", [
        "hey", "social anxiety hai mujhe", "logo ke saamne jaane mein darr",
        "class mein baat nahi kar pata", "viva mein freeze ho jata hu",
        "judge hone ka darr hai", "kaise theek hoga yeh",
        "haan try karna chahta hu", "okay thanks", "bye"
    ]),
    ("S017", "anxiety", [
        "hello", "burnout ho gaya hu completely", "workload bohot hai",
        "din mein 14 ghante padhai", "rest ka time nahi milta",
        "body tense rehti hai", "sar mein dard rehta hai",
        "kya karu balance ke liye", "haan", "thanks", "bye"
    ]),
    ("S018", "anxiety", [
        "hi bhai", "raat ko neend nahi aati", "soch soch ke dimag kharab",
        "worst case scenarios dimaag mein aate rehte hain",
        "agar fail ho gaya toh", "agar job nahi mili toh",
        "kaise band karu overthinking", "tips de na",
        "haan try karta hu", "thanks yar"
    ]),
    ("S019", "anxiety", [
        "hey", "bohot irritable ho gaya hu", "chhoti chhoti baaton pe gussa",
        "patience khatam ho gayi", "sab se ladai ho jaati hai",
        "lagta hai main anger issues wala hu", "control nahi hota",
        "koi help karo", "haan", "okay try karta hu", "bye"
    ]),
    ("S020", "anxiety", [
        "hi", "exam hall mein anxiety hoti hai", "paper dekhte hi blank ho jata hu",
        "sab kuch bhool jata hu", "haath kaanpne lagte hain",
        "result ka bohot darr hai", "agar compartment aa gayi toh",
        "mummy papa kya kahenge", "tips de padhai ke liye",
        "haan", "thanks bhai", "bye"
    ]),
]

# TOPIC 3: LONELINESS (10 students)
LONELINESS_CONVOS = [
    ("S021", "loneliness", [
        "hi", "bohot akela feel hota hai", "hostel mein koi dost nahi",
        "ghar ki yaad aa rahi hai", "maa se baat karna chahta hu",
        "roommate bhi ignore karta hai", "lunch akele khata hu roz",
        "kya karu dost kaise banau", "haan try karunga", "thanks", "bye"
    ]),
    ("S022", "loneliness", [
        "hello", "i feel so lonely", "nobody talks to me in class",
        "i sit alone everywhere", "even on my birthday nobody wished me",
        "i think people dont like me", "am i that boring",
        "what should i do", "haan", "okay thanks", "bye"
    ]),
    ("S023", "loneliness", [
        "hey", "mera koi dost nahi hai", "sab ne mujhe chhod diya",
        "trust karna band kar diya maine", "log dhoka dete hain",
        "akele rehna seekh liya hai", "par dard toh hota hai",
        "kya main hamesha akela rahunga", "haan", "thanks", "bye"
    ]),
    ("S024", "loneliness", [
        "hi bhai", "college mein new hu", "kisi se baat nahi hoti",
        "sab groups already ban chuke hain", "main outsider hu",
        "canteen mein akela baithta hu", "fest mein koi saath nahi gaya",
        "bohot difficult hai adjust karna", "tips de na",
        "haan", "thanks yar", "bye"
    ]),
    ("S025", "loneliness", [
        "namaste", "papa se rishta achha nahi hai", "ghar mein baat nahi hoti",
        "mummy busy rehti hain", "bhai apni duniya mein hai",
        "ghar jaake bhi akela lagta hai", "koi sunne wala nahi hai",
        "kya karu main", "haan", "okay try karunga", "bye"
    ]),
    ("S026", "loneliness", [
        "hello", "mera phone kabhi nahi bajta", "social media pe sab ke dost hain",
        "mere kisi ki story mein tag nahi hota", "group photos mein main nahi hota",
        "invisible hu sabke liye", "kya galat hai mere mein",
        "haan batao kya karu", "okay", "thanks", "bye"
    ]),
    ("S027", "loneliness", [
        "hi", "weekend pe bhi koi plan nahi hota", "akele ghar pe baitha rehta hu",
        "bahar jaane ka mann nahi karta", "koi baat nahi karta",
        "khud se baat karta hu akele mein", "pagal toh nahi ho raha",
        "kaise change karu yeh", "haan", "thanks bhai", "bye"
    ]),
    ("S028", "loneliness", [
        "hey", "project ke liye koi partner nahi mila",
        "sab apne groups mein hain", "professor bhi puchte hain",
        "bohot embarrassing hai", "no one wants to work with me",
        "main kya karu ab", "haan", "okay thanks", "bye"
    ]),
    ("S029", "loneliness", [
        "hi", "raat ko sab so jaate hain main jagta rehta hu",
        "3 baje tak phone chalata hu", "neend nahi aati akele mein",
        "koi baat karne wala nahi hota raat ko", "deewar se baat karta hu",
        "yeh normal hai kya", "haan", "music suna de", "thanks", "bye"
    ]),
    ("S030", "loneliness", [
        "hello bhai", "mujhse pyar koi nahi karta", "koi hug nahi karta",
        "touch starved feel ho raha hai", "koi apna nahi lagta",
        "mujhe abandon kar diya sabne", "kya main itna bura hu",
        "help karo please", "haan", "thanks", "bye"
    ]),
]

# TOPIC 4: ACADEMIC PRESSURE (10 students)
ACADEMIC_CONVOS = [
    ("S031", "academic", [
        "hi", "exam mein fail ho gaya bhai", "marks bohot kam aaye",
        "papa bohot naraz hain", "mummy ro rahi thi",
        "sabse zyada dard yeh hai ki mehnat ki thi",
        "kya fayda hua padhai ka", "ab kya karu",
        "haan", "tips de study ke", "thanks", "bye"
    ]),
    ("S032", "academic", [
        "hello", "placement nahi ho rahi", "sab dost select ho gaye",
        "main reh gaya", "resume mein kya daalu", "skills nahi hain",
        "8 companies mein reject ho gaya", "bohot frustrated hu",
        "kya karu ab", "haan", "thanks", "bye"
    ]),
    ("S033", "academic", [
        "hey bhai", "cgpa gir gaya is semester", "backlog bhi lag gayi",
        "ghar waale kya kahenge", "papa ne fees di thi",
        "usne toh itna mehnat kiya mere liye", "main fail ho gaya",
        "drop year lena chahiye kya", "haan batao", "thanks", "bye"
    ]),
    ("S034", "academic", [
        "hi", "syllabus khatam nahi ho raha", "exam next week hai",
        "aadha bhi nahi padha", "kaise karunga complete",
        "panic ho raha hai", "neend bhi nahi aa rahi",
        "padhai mein mann nahi lagta", "tips de focus ke liye",
        "haan", "try karta hu", "bye"
    ]),
    ("S035", "academic", [
        "namaste", "competitive exam ki tayyari kar raha hu",
        "2 saal se padh raha hu", "result nahi aa raha",
        "dost sab settle ho gaye", "main abhi bhi padh raha hu",
        "kab tak padhun", "haar maan lu kya", "nahi",
        "motivation de do", "thanks bhai", "bye"
    ]),
    ("S036", "academic", [
        "hello", "coaching bohot hectic hai", "subah 6 se raat 10 baje tak",
        "khud ke liye time nahi milta", "health bhi kharab ho rahi",
        "friends se milna band ho gaya", "kya yeh worth it hai",
        "haan", "okay", "thanks", "bye"
    ]),
    ("S037", "academic", [
        "hi bhai", "viva mein kuch nahi bola paya", "professor ne daanta",
        "sab ke saamne insult kiya", "bohot sharminda hu",
        "class mein jaane ka mann nahi karta ab", "i hate my college",
        "kya karu", "haan", "okay try karta hu", "bye"
    ]),
    ("S038", "academic", [
        "hey", "online classes samajh nahi aati", "professor bohot fast padhate hain",
        "notes bhi nahi hain", "dost se maangta hu toh bhi incomplete",
        "library mein jagah nahi milti", "kaise padhu bata",
        "haan", "try karta hu", "thanks", "bye"
    ]),
    ("S039", "academic", [
        "hi", "mummy papa ke expectations bohot high hain",
        "engineer banna hai unhe par mujhe nahi", "mera interest arts mein hai",
        "par woh sunne ko tayaar nahi", "force kar rahe hain",
        "main khush nahi hu yahan", "kya karu",
        "haan", "thanks for listening", "bye"
    ]),
    ("S040", "academic", [
        "hello", "attendance kam hai bohot", "debarred ho jaunga shayad",
        "class mein jaane ka mann nahi karta", "boring lagta hai sab",
        "kisi cheez mein interest nahi raha", "padhai chhodna chahta hu",
        "par ghar waale", "kya karu main", "haan", "bye"
    ]),
]

# TOPIC 5: RELATIONSHIPS & HEARTBREAK (10 students)
RELATIONSHIP_CONVOS = [
    ("S041", "relationship", [
        "hi", "mera breakup ho gaya bhai", "3 saal ki relationship thi",
        "usne dhoka diya", "kisi aur ke saath hai ab",
        "bohot dard ho raha hai", "move on nahi ho pa raha",
        "kya karu yar", "haan", "music suna de", "thanks", "bye"
    ]),
    ("S042", "relationship", [
        "hello", "crush ne friendzone kar diya", "proposal reject ho gaya",
        "usse bohot pyar karta tha", "sab kuch de diya",
        "ab kya fayda", "one sided love khatam", "dil toot gaya",
        "haan", "movie suggest kar", "thanks", "bye"
    ]),
    ("S043", "relationship", [
        "hey bhai", "ex ko bhool nahi pa raha", "roz unki yaad aati hai",
        "gaano mein unki yaad aati hai", "unka number delete nahi kar pa raha",
        "unke photos dekh ke rona aata hai", "kaise bhulu unhe",
        "tips de na", "haan", "try karunga", "bye"
    ]),
    ("S044", "relationship", [
        "hi", "relationship toxic thi", "usne manipulate kiya mujhe",
        "bohot possessive tha", "friends se milne nahi deta tha",
        "phone check karta tha", "abusive relationship thi",
        "ab break up kar liya par trauma hai", "kya karu",
        "haan", "thanks", "bye"
    ]),
    ("S045", "relationship", [
        "namaste", "pyar mein vishwas nahi raha", "2 baar dhoka mila",
        "ab kisi pe bharosa nahi hoga", "pyar ek dhoka hai",
        "sabko bas matlabi hai", "kya main kabhi khush ho paunga",
        "haan", "okay", "thanks", "bye"
    ]),
    ("S046", "relationship", [
        "hello", "gf ne block kar diya mujhe", "koi reason nahi bataya",
        "messages bhi nahi padhe", "mutual friends ne bhi side le liya",
        "bohot alone feel ho raha hai", "kya galti thi meri",
        "kya karu ab", "haan", "thanks bhai", "bye"
    ]),
    ("S047", "relationship", [
        "hey", "long distance relationship mein problems hain",
        "woh busy rehti hai", "mujhse baat nahi karti",
        "lagta hai interest kho diya usne", "kya main clingy hu",
        "space dena chahiye kya", "confused hu bohot",
        "haan", "okay thanks", "bye"
    ]),
    ("S048", "relationship", [
        "hi bhai", "best friend ne backstab kiya",
        "mere secrets sabko bata diye", "ab poora group uski side pe hai",
        "meri dosti kharab ho gayi", "trust tod diya usne",
        "bohot hurt hu", "kya karu", "haan", "thanks", "bye"
    ]),
    ("S049", "relationship", [
        "hello", "valentine day aa raha hai", "sab couple hain main akela",
        "ek baar bhi kisi ne propose nahi kiya", "kya main itna bura hu",
        "self esteem bohot low hai", "kya koi mujhse pyar karega kabhi",
        "haan", "music suna de", "thanks", "bye"
    ]),
    ("S050", "relationship", [
        "hi", "parents ka rishta kharab hai", "roz ladai hoti hai ghar mein",
        "papa chillate hain mummy roti hain", "main kamre mein chala jata hu",
        "darr lagta hai", "unka divorce ho jayega kya",
        "kya karu main", "haan", "thanks bhai", "bye"
    ]),
]

# TOPIC 6: ABUSE & SAFETY (10 students)
ABUSE_CONVOS = [
    ("S051", "abuse", [
        "hi", "mujhe ek baat batani hai", "mere uncle ne mujhe galat touch kiya",
        "bohot darr lagta hai unse", "kisi ko bata nahi sakti",
        "mummy ko batau toh vishwas nahi karegi", "kya karu main",
        "haan", "police ko batau kya", "okay", "thanks"
    ]),
    ("S052", "abuse", [
        "hello bhai", "college mein ragging hoti hai", "seniors bohot maarte hain",
        "hostel mein darr ke rehta hu", "raat ko bhi aate hain room mein",
        "complaint karu toh aur marenge", "safe nahi hu yahan",
        "help chahiye", "haan", "okay thanks", "bye"
    ]),
    ("S053", "abuse", [
        "hey", "papa bohot maarte hain", "chhoti chhoti baaton pe maar padti hai",
        "belt se maarte hain kabhi kabhi", "mummy bhi nahi rok paati",
        "ghar jaane mein darr lagta hai", "kya yeh normal hai",
        "nahi nahi yeh galat hai", "kya karu", "haan", "okay thanks"
    ]),
    ("S054", "abuse", [
        "hi", "online harassment ho rahi hai", "koi fake account se messages bhejta hai",
        "gandi gandi photos bhejta hai", "blackmail kar raha hai",
        "mere photos leak karne ki dhamki de raha hai",
        "bohot darr lagta hai", "police ko batau",
        "haan", "okay thanks bhai"
    ]),
    ("S055", "abuse", [
        "hello", "mera molestation hua hai", "padosi ne kiya",
        "main bohot chhota tha tab", "aaj tak kisiko bataya nahi",
        "bohot sharam aati hai", "kya meri galti hai",
        "nahi nahi bilkul nahi", "thanks for saying that", "bye"
    ]),
    ("S056", "abuse", [
        "hey bhai", "school mein bully karte hain sab",
        "class mein hasate hain", "naam se nahi nickname se bulate hain",
        "canteen mein khaana chhin lete hain", "teacher ko bataya toh kuch nahi hua",
        "bohot frustrated hu", "kya karu", "haan", "okay thanks", "bye"
    ]),
    ("S057", "abuse", [
        "hi", "eve teasing hoti hai roz", "college ke bahar ladke comment karte hain",
        "darr lagta hai akele jaane mein", "friends ke saath jati hu par phir bhi",
        "kya koi safe nahi hai", "complaint karu toh log kya kahenge",
        "haan", "okay", "thanks"
    ]),
    ("S058", "abuse", [
        "namaste", "ghar mein domestic violence hoti hai", "papa mummy ko maarte hain",
        "main rok nahi pata", "bohot helpless feel hota hai",
        "darr lagta hai ki mujhe bhi maarenge", "kya karu",
        "police bulau kya", "haan", "thanks", "bye"
    ]),
    ("S059", "abuse", [
        "hello", "teacher ne galat tarike se touch kiya",
        "class ke baad roka tha", "bohot uncomfortable tha",
        "principal ko batau toh teacher powerful hai",
        "proof nahi hai mere paas", "koi manega nahi",
        "haan", "okay try karta hu", "thanks"
    ]),
    ("S060", "abuse", [
        "hi bhai", "cyber bullying ho rahi hai", "classmates trolls karte hain",
        "mere photos edit karke group mein daale hain",
        "bohot humiliated feel ho raha hai", "school jaane ka mann nahi karta",
        "parents ko batau kya", "haan", "okay", "thanks bhai"
    ]),
]

# TOPIC 7: SUICIDAL THOUGHTS / CRISIS (10 students)
CRISIS_CONVOS = [
    ("S061", "crisis", [
        "hi", "mujhe koi samajhta nahi", "bohot thak gaya hu sab se",
        "lagta hai mera koi fayda nahi", "i want to die",
        "haan seriously", "mujhe help chahiye", "okay",
        "haan call karta hu", "thanks"
    ]),
    ("S062", "crisis", [
        "hello bhai", "ab aur nahi jhela jata", "zindagi se tang aa gaya hu",
        "sab kuch khatam karna chahta hu", "koi bachane wala nahi hai",
        "haan", "okay helpline pe call karta hu", "thanks"
    ]),
    ("S063", "crisis", [
        "hey", "i want to kill myself", "i have no reason to live",
        "nobody would miss me", "i already wrote a note",
        "haan seriously", "okay", "call karta hu abhi"
    ]),
    ("S064", "crisis", [
        "hi", "jeene ka mann nahi hai", "sab kuch bekar hai",
        "mar jana better lagta hai", "zahar kha lu kya",
        "nahi nahi seriously puch raha hu", "okay",
        "haan abhi call karta hu", "thanks bhai"
    ]),
    ("S065", "crisis", [
        "hello", "i want to sleep and never wake up",
        "everything is so painful", "i cant take it anymore",
        "the world is better without me", "dont try to stop me",
        "okay fine ill call", "thanks"
    ]),
    ("S066", "crisis", [
        "bhai", "maine goliyan kha li hain", "bohot neend aa rahi hai",
        "sab blur dikh raha hai", "please help",
        "okay hospital", "thanks"
    ]),
    ("S067", "crisis", [
        "hi", "i cut myself today", "its not the first time",
        "it feels like the only way to feel something",
        "i know its wrong", "par ruk nahi pata",
        "help chahiye", "haan", "okay", "thanks"
    ]),
    ("S068", "crisis", [
        "hello", "duniya chhod ke jana chahta hu",
        "kisi ko farak nahi padega", "alvida duniya",
        "haan", "okay thik hai", "call karta hu"
    ]),
    ("S069", "crisis", [
        "hi bhai", "bohot pareshan hu", "padhai nahi ho rahi",
        "ghar pe ladai ho rahi hai", "breakup bhi ho gaya",
        "sab ek saath aa gaya", "ab nahi jhela jata",
        "mar jau kya", "nahi par", "okay call karta hu", "thanks"
    ]),
    ("S070", "crisis", [
        "hey", "aaj raat ke baad sab khatam", "yeh meri aakhri baat hai",
        "kisi ko farak nahi padega", "mera jaana better hai",
        "nahi", "okay sun raha hu", "thik hai call karta hu"
    ]),
]

# TOPIC 8: SLEEP ISSUES (10 students)
SLEEP_CONVOS = [
    ("S071", "sleep", [
        "hi", "neend nahi aa rahi yar", "raat bhar jaagta hu",
        "3-4 ghante hi so pata hu", "din mein thaka rehta hu",
        "coffee se bhi kuch nahi hota", "kya karu",
        "haan", "try karta hu", "thanks", "bye"
    ]),
    ("S072", "sleep", [
        "hello", "insomnia hai mujhe", "2 hafto se properly soya nahi",
        "neend ki goliyan le raha hu", "par habit nahi banani chahiye",
        "natural tarike se kaise sou", "tips de na",
        "haan", "okay try karta hu", "thanks", "bye"
    ]),
    ("S073", "sleep", [
        "hey bhai", "bure sapne aate hain raat ko", "darr ke uth jata hu",
        "phir neend nahi aati", "raat ko akele darr lagta hai",
        "sleep paralysis bhi hota hai kabhi kabhi",
        "bohot scary hai", "kya karu", "haan", "thanks", "bye"
    ]),
    ("S074", "sleep", [
        "hi", "mera sleep cycle bigad gaya hai", "raat ko 4 baje sota hu",
        "subah 12 baje uthta hu", "classes miss ho rahi hain",
        "attendance kam ho gayi", "kaise fix karu",
        "haan", "try karta hu", "thanks", "bye"
    ]),
    ("S075", "sleep", [
        "namaste", "bohot zyada so raha hu", "12-14 ghante so jata hu",
        "phir bhi thaka rehta hu", "energy nahi hai kuch karne ki",
        "kya depression ki wajah se hai", "haan",
        "okay", "thanks bhai", "bye"
    ]),
    ("S076", "sleep", [
        "hello", "overthinking ki wajah se neend nahi aati",
        "sone se pehle dimaag mein hazar cheezein aati hain",
        "kal kya hoga sochta rehta hu", "raat ko anxiety badhti hai",
        "kaise stop karu", "haan", "try karunga", "thanks", "bye"
    ]),
    ("S077", "sleep", [
        "hi bhai", "phone ki wajah se neend nahi aati",
        "puri raat reels dekhta rehta hu", "subah pachtata hu",
        "addiction hai yeh", "phone nahi rakh pata ratko",
        "kya karu", "haan", "okay screen time set karta hu", "bye"
    ]),
    ("S078", "sleep", [
        "hey", "neend mein baat karta hu", "roommate ne bataya",
        "sleepwalking bhi ki hai ek baar", "kya kuch serious toh nahi",
        "doctor ko dikhau kya", "haan",
        "okay appointment leta hu", "thanks", "bye"
    ]),
    ("S079", "sleep", [
        "hi", "exam ke time neend hi nahi aati",
        "padh padh ke thak jata hu par neend nahi",
        "aankhen jal rahi hain", "sar mein dard hai",
        "kaise sou jaldi tips de", "haan",
        "okay 4-7-8 try karta hu", "thanks bhai", "bye"
    ]),
    ("S080", "sleep", [
        "hello", "raat ko baar baar uth jata hu",
        "2-3 baar toh zaroor", "washroom bhi nahi jaana hota",
        "bas uth jata hu beech neend mein", "phir sone mein time lagta hai",
        "frustrating hai bohot", "tips de na",
        "haan", "okay try karta hu", "bye"
    ]),
]

# TOPIC 9: FAMILY ISSUES (10 students)
FAMILY_CONVOS = [
    ("S081", "family", [
        "hi", "ghar pe bohot ladai hoti hai", "mummy papa ka roz jhagda",
        "main kamre mein chhup jata hu", "bohot darr lagta hai",
        "unka divorce ho jayega kya", "kya karu",
        "haan", "okay thanks", "bye"
    ]),
    ("S082", "family", [
        "hello bhai", "papa bohot strict hain", "mobile nahi dete",
        "friends se milne nahi dete", "padhai padhai padhai bas",
        "bohot suffocating hai ghar", "bhaag jaana chahta hu",
        "haan", "nahi nahi bhaagunga nahi", "thanks", "bye"
    ]),
    ("S083", "family", [
        "hey", "mummy samajhti nahi hai", "kehti hai drama kar raha hai",
        "depression fake hai unke liye", "dawa nahi dila rahi",
        "papa ko lagta hai pagal hu", "koi support nahi hai ghar pe",
        "kya karu", "haan", "thanks", "bye"
    ]),
    ("S084", "family", [
        "hi", "bhai se compare karte hain roz", "woh topper hai main average",
        "padosi ke bete se bhi compare", "tujhse kuch nahi hoga kehte hain",
        "self confidence zero hai mera", "kaise handle karu",
        "haan", "try karunga", "thanks", "bye"
    ]),
    ("S085", "family", [
        "namaste", "ghar mein paise ki bohot dikkat hai",
        "papa ki dukaan band ho gayi", "fees ke paise nahi hain",
        "scholarship ke liye apply kiya par mili nahi",
        "part time job karu kya", "kya karu bata na",
        "haan", "okay try karta hu", "bye"
    ]),
    ("S086", "family", [
        "hello", "papa sharaab peete hain roz", "peeke ghar aate hain",
        "mummy ko gaaliyan dete hain", "kabhi kabhi maarte bhi hain",
        "main rok nahi pata", "bohot helpless hu",
        "kya karu", "haan", "thanks", "bye"
    ]),
    ("S087", "family", [
        "hi bhai", "parents ne forced marriage kar rahe hain",
        "abhi toh padhai chal rahi hai", "par unhe jaldi shaadi karwani hai",
        "meri marzi ki koi value nahi", "bohot pressure hai",
        "kya karu", "haan", "thanks", "bye"
    ]),
    ("S088", "family", [
        "hey", "dadi ka demise ho gaya", "bohot close the hum",
        "rona band nahi ho raha", "ghar mein sab toot gaye hain",
        "unke bina sab suna lagta hai", "kaise deal karun",
        "haan", "thanks", "bye"
    ]),
    ("S089", "family", [
        "hi", "mummy hospital mein hai", "operation hona hai",
        "bohot darr lagta hai", "kya hoga pata nahi",
        "papa bhi bohot tense hain", "main strong ban ke dikha raha hu",
        "par andar se toot raha hu", "kya karu",
        "haan", "thanks bhai", "bye"
    ]),
    ("S090", "family", [
        "hello", "parents ka divorce final ho gaya",
        "court mein jaana padta hai", "dono taraf se pressure hai",
        "kiski side lu samajh nahi aa raha", "bohot confused hu",
        "help karo please", "haan", "thanks", "bye"
    ]),
]

# TOPIC 10: HAPPY / POSITIVE (10 students)
HAPPY_CONVOS = [
    ("S091", "happy", [
        "hi bhai", "aaj bohot achha din hai", "exam mein achhe marks aaye",
        "mummy ne hug kiya", "papa ne bike dilwane ka bola",
        "bohot khush hu", "best day ever", "thanks yar", "bye"
    ]),
    ("S092", "happy", [
        "hello", "placement ho gayi bhai", "google mein lagi hai",
        "sapna poora ho gaya", "family bohot khush hai",
        "party hai aaj raat ko", "life is lit", "thanks", "bye"
    ]),
    ("S093", "happy", [
        "hey", "crush ne haan bol diya", "propose accept ho gaya",
        "i am so happy", "duniya mein sabse khush main hu",
        "celebration kaise karu", "haan", "thanks bhai", "bye"
    ]),
    ("S094", "happy", [
        "hi", "first salary aayi hai aaj", "bohot amazing feel ho raha hai",
        "mummy ke liye gift liya", "papa ke liye bhi",
        "self made feel ho raha hai", "life is good", "thanks", "bye"
    ]),
    ("S095", "happy", [
        "namaste", "college fest mein prize jeeta", "first rank aaya",
        "teacher ne bohot appreciate kiya", "friends ne treat diya",
        "achha lagta hai jab mehnat ka result milta hai", "thanks", "bye"
    ]),
    ("S096", "happy", [
        "hello bhai", "ghar ja raha hu chutti mein", "bohot excitement hai",
        "mummy ka khaana kha lunga", "sab se milne ka mann hai",
        "ghar jaisa kuch nahi hota", "thanks bhai", "bye"
    ]),
    ("S097", "happy", [
        "hey", "naya hobby start kiya hai painting", "bohot relaxing hai",
        "talent hai mujhme", "friends ne bhi appreciate kiya",
        "life mein kuch achha ho raha hai finally", "thanks", "bye"
    ]),
    ("S098", "happy", [
        "hi", "gym se wapas aaya hu", "bohot achha feel ho raha hai",
        "energy high hai", "body mein confidence aa raha hai",
        "workout is the best therapy", "haan", "thanks bhai", "bye"
    ]),
    ("S099", "happy", [
        "hello", "aaj bohot positive feel ho raha hai",
        "sab kuch theek chal raha hai", "padhai bhi achhi ja rahi hai",
        "friends bhi achhe hain", "family bhi support karti hai",
        "grateful feel ho raha hai", "thanks", "bye"
    ]),
    ("S100", "happy", [
        "hi bhai", "internship mein achha review aaya",
        "manager ne praise kiya", "team mein sabse achha kaam kiya",
        "confidence badh gaya hai", "career mein positive direction",
        "sab badhiya hai", "thanks yar", "bye"
    ]),
]

# Combine all conversations
ALL_CONVERSATIONS = (
    DEPRESSION_CONVOS + ANXIETY_CONVOS + LONELINESS_CONVOS +
    ACADEMIC_CONVOS + RELATIONSHIP_CONVOS + ABUSE_CONVOS +
    CRISIS_CONVOS + SLEEP_CONVOS + FAMILY_CONVOS + HAPPY_CONVOS
)

if __name__ == "__main__":
    total_msgs = sum(len(msgs) for _, _, msgs in ALL_CONVERSATIONS)
    print(f"Total students: {len(ALL_CONVERSATIONS)}")
    print(f"Total messages: {total_msgs}")
    print(f"Estimated report lines (x10 per msg): ~{total_msgs * 10}")
    for topic in ["depression", "anxiety", "loneliness", "academic",
                   "relationship", "abuse", "crisis", "sleep", "family", "happy"]:
        count = sum(1 for _, t, _ in ALL_CONVERSATIONS if t == topic)
        msgs = sum(len(m) for _, t, m in ALL_CONVERSATIONS if t == topic)
        print(f"  {topic}: {count} students, {msgs} messages")
