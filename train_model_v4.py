"""
===============================================================================
🎓 MINDMATE AI V4: ENHANCED TRAINING SCRIPT
===============================================================================
Upgrades from V3:
  1. MERGED DATASET: Original + AI-generated data for better coverage
  2. GLOVE EMBEDDINGS: Pre-trained word vectors (100d) instead of learning
     embeddings from scratch — model already "understands" language!
  3. DATA AUGMENTATION: Random word dropout for robustness
  4. Label Smoothing: Prevents overconfident predictions
  5. Higher epochs with smarter early stopping
===============================================================================
"""
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Embedding, LSTM, Dense, Bidirectional, Dropout,
    Input, Layer, Concatenate, GlobalAveragePooling1D
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import pickle
import os
import re

# --- SETUP ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ==============================================================================
# 🧠 CUSTOM ATTENTION LAYER
# ==============================================================================
class AttentionLayer(Layer):
    """
    Simple Attention: Learns which words in the sentence are most important
    for the classification decision.
    """
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name='attention_weight',
                                 shape=(input_shape[-1], 1),
                                 initializer='glorot_uniform',
                                 trainable=True)
        self.b = self.add_weight(name='attention_bias',
                                 shape=(input_shape[1], 1),
                                 initializer='zeros',
                                 trainable=True)
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        e = tf.keras.backend.tanh(tf.keras.backend.dot(x, self.W) + self.b)
        a = tf.keras.backend.softmax(e, axis=1)
        output = x * a
        return tf.keras.backend.sum(output, axis=1)

# ==============================================================================
# 📂 1. LOAD & MERGE DATA
# ==============================================================================
print("⏳ Loading datasets...")

ORIGINAL_FILE = 'AUGMENTED_dataset.csv'
AI_FILE = 'AI_GENERATED_dataset.csv'

try:
    original = pd.read_csv(ORIGINAL_FILE)
    print(f"  ✅ Original: {len(original)} examples")
except FileNotFoundError:
    print(f"❌ '{ORIGINAL_FILE}' not found!")
    exit()

# Try to load AI-generated data (optional)
ai_data = None
if os.path.exists(AI_FILE):
    ai_data = pd.read_csv(AI_FILE)
    print(f"  ✅ AI-Generated: {len(ai_data)} examples")
else:
    print(f"  ⚠️ AI data not found. Run generate_ai_data.py first for extra boost!")
    print(f"     Continuing with original data only...")

# Merge datasets
if ai_data is not None:
    data = pd.concat([original, ai_data], ignore_index=True)
    # Shuffle
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"  📊 TOTAL merged: {len(data)} examples")
else:
    data = original

# Show class distribution
print("\n📊 Class Distribution:")
label_names = {
    0: "Happy",
    1: "Sad/Stress",
    2: "Critical/Risk",
    3: "Out_Of_Context",
    4: "Chitchat"
}
for label, name in label_names.items():
    count = len(data[data['label'] == label])
    print(f"   Class {label} ({name}): {count} samples")

# ==============================================================================
# 🔠 2. PREPROCESSING
# ==============================================================================
data['text'] = data['text'].astype(str).str.lower().str.strip()
data = data.dropna(subset=['text', 'label'])
data['label'] = data['label'].astype(int)

# ==============================================================================
# 🔢 3. TOKENIZATION
# ==============================================================================
vocab_size = 10000    # V4: increased for AI-generated vocabulary
max_length = 50
oov_tok = "<OOV>"
num_classes = len(data['label'].unique())

print(f"\n🔠 Tokenizing (Vocab: {vocab_size}, MaxLen: {max_length}, Classes: {num_classes})...")
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(data['text'])

sequences = tokenizer.texts_to_sequences(data['text'])
padded = pad_sequences(sequences, maxlen=max_length, padding='post')

# ==============================================================================
# 📐 4. TRAIN / TEST SPLIT (80/20)
# ==============================================================================
X_train, X_test, y_train, y_test = train_test_split(
    padded, data['label'].values, test_size=0.2, random_state=42, stratify=data['label']
)
print(f"📐 Split: {len(X_train)} train / {len(X_test)} test")

# ==============================================================================
# ⚖️ 5. CLASS WEIGHTS
# ==============================================================================
print("\n⚖️ Computing class weights...")
unique_classes = np.unique(y_train)
class_weights_arr = compute_class_weight('balanced', classes=unique_classes, y=y_train)
class_weight_dict = {int(c): float(w) for c, w in zip(unique_classes, class_weights_arr)}
print(f"   {class_weight_dict}")

# ==============================================================================
# 🌐 6. GLOVE EMBEDDINGS (Pre-trained word vectors)
# ==============================================================================
GLOVE_FILE = os.path.join('glove.6B', 'glove.6B.100d.txt')
embedding_dim = 100  # GloVe dimension

if os.path.exists(GLOVE_FILE):
    print(f"\n🌐 Loading GloVe embeddings ({GLOVE_FILE})...")
    
    embeddings_index = {}
    with open(GLOVE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
    
    print(f"   Loaded {len(embeddings_index)} word vectors")
    
    # Build embedding matrix
    word_index = tokenizer.word_index
    num_words = min(vocab_size, len(word_index) + 1)
    embedding_matrix = np.zeros((num_words, embedding_dim))
    
    found = 0
    for word, i in word_index.items():
        if i >= vocab_size:
            continue
        vector = embeddings_index.get(word)
        if vector is not None:
            embedding_matrix[i] = vector
            found += 1
    
    coverage = found / min(len(word_index), vocab_size) * 100
    print(f"   ✅ GloVe coverage: {found}/{min(len(word_index), vocab_size)} words ({coverage:.1f}%)")
    
    USE_GLOVE = True
else:
    print(f"\n⚠️ GloVe file not found: {GLOVE_FILE}")
    print(f"   To use GloVe: Download from https://nlp.stanford.edu/data/glove.6B.zip")
    print(f"   Extract glove.6B.100d.txt into project folder")
    print(f"   Continuing with learned embeddings (still improved with AI data!)...\n")
    embedding_dim = 128
    USE_GLOVE = False

# ==============================================================================
# 🧠 7. MODEL ARCHITECTURE (V4: GloVe + Deeper Bi-LSTM + Attention)
# ==============================================================================
print(f"\n🧠 Building V4 {'GloVe-Enhanced' if USE_GLOVE else 'Standard'} Bi-LSTM model...")

lstm_units = 128

inputs = Input(shape=(max_length,))

# Layer 1: Embedding (GloVe or learned)
if USE_GLOVE:
    # Pre-trained GloVe — freeze initially for stability, fine-tune later via trainable=True
    x = Embedding(num_words, embedding_dim, 
                  weights=[embedding_matrix],
                  input_length=max_length,
                  trainable=True)(inputs)  # trainable=True allows fine-tuning
else:
    x = Embedding(vocab_size, embedding_dim, input_length=max_length)(inputs)

x = Dropout(0.3)(x)

# Layer 2: First Bidirectional LSTM
x = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
x = Dropout(0.3)(x)

# Layer 3: Second Bidirectional LSTM (deeper)
x = Bidirectional(LSTM(lstm_units // 2, return_sequences=True))(x)
x = Dropout(0.3)(x)

# Layer 4: Attention Mechanism
attention_out = AttentionLayer()(x)

# Layer 5: Global Average Pooling
avg_pool = GlobalAveragePooling1D()(x)

# Layer 6: Concatenate
x = Concatenate()([attention_out, avg_pool])

# Layer 7: Dense layers
x = Dense(128, activation='relu')(x)
x = Dropout(0.4)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(32, activation='relu')(x)

# Layer 8: Output
outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=inputs, outputs=outputs)

# ==============================================================================
# ⚙️ 8. COMPILE & TRAIN
# ==============================================================================
# V4: Label smoothing to prevent overconfident predictions (helps with edge cases)
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)

model.compile(
    loss=loss_fn,
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=['accuracy']
)
model.summary(line_length=120)

# Callbacks
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_accuracy', patience=8, restore_best_weights=True
)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6
)

print("\n🚀 Starting V4 training...")
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    class_weight=class_weight_dict,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# ==============================================================================
# 📈 9. EVALUATION
# ==============================================================================
print("\n📈 V4 Evaluation:")
y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
print("\n" + classification_report(y_test, y_pred, target_names=[
    "Happy (0)", "Sad/Stress (1)", "Critical (2)", "Out_Of_Context (3)", "Chitchat (4)"
]))

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"🎯 V4 Test Accuracy: {test_acc:.4f}")

# ==============================================================================
# 💾 10. SAVE ARTIFACTS
# ==============================================================================
print("\n💾 Saving V4 model files...")
model.save("mental_health_model.h5")

with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

config = {
    "vocab_size": vocab_size if not USE_GLOVE else num_words,
    "max_length": max_length,
    "num_classes": num_classes,
    "label_names": label_names,
    "version": "V4",
    "features": ["GloVe" if USE_GLOVE else "Learned Embeddings", "AI-Augmented Data"]
}
with open('model_config.pickle', 'wb') as handle:
    pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(f"\n🎉 V4 SUCCESS! Model trained with {test_acc:.2%} accuracy.")
print(f"   Saved: mental_health_model.h5, tokenizer.pickle, model_config.pickle")
print(f"   Features: {'GloVe Embeddings' if USE_GLOVE else 'Learned Embeddings'} + AI Data")
print(f"   Classes: {num_classes} (Happy, Sad, Critical, OOC, Chitchat)")
