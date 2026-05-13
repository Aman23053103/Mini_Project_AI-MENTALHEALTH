"""
===============================================================================
🎓 MINDMATE AI V3: TRAINING SCRIPT
===============================================================================
Upgrades from V2:
  - 5 classes: Happy, Sad, Critical, Out_Of_Context, Chitchat
  - Augmented dataset with failure injection + synonym augmentation
  - Deeper architecture (2 LSTM layers)
  - Higher vocab (8000) and max_length (50)
  - Class weights for balanced learning
  - Context-aware data preprocessing
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
# 📂 1. LOAD DATA
# ==============================================================================
print("⏳ Loading augmented dataset...")
DATASET_FILE = 'AUGMENTED_dataset.csv'

try:
    data = pd.read_csv(DATASET_FILE)
    print(f"✅ Dataset loaded! Found {len(data)} examples.")
except FileNotFoundError:
    print(f"❌ Error: '{DATASET_FILE}' not found. Run augment_dataset.py first!")
    exit()

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
data['text'] = data['text'].astype(str).str.lower()
data['text'] = data['text'].str.strip()
data = data.dropna(subset=['text', 'label'])
data['label'] = data['label'].astype(int)

# ==============================================================================
# 🔢 3. TOKENIZATION (V3: larger vocab + longer sequences)
# ==============================================================================
vocab_size = 8000     # V3: increased from 5000 for richer Hinglish vocabulary
max_length = 50       # V3: increased from 30 for longer sentences
oov_tok = "<OOV>"
num_classes = len(data['label'].unique())

print(f"\n🔠 Tokenizing text (Vocab: {vocab_size}, MaxLen: {max_length}, Classes: {num_classes})...")
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
print(f"📐 Split: {len(X_train)} train / {len(X_test)} test samples")

# ==============================================================================
# ⚖️ 5. CLASS WEIGHTS (handle imbalanced data)
# ==============================================================================
print("\n⚖️ Computing class weights for balanced learning...")
unique_classes = np.unique(y_train)
class_weights_arr = compute_class_weight('balanced', classes=unique_classes, y=y_train)
class_weight_dict = {int(c): float(w) for c, w in zip(unique_classes, class_weights_arr)}
print(f"   Class weights: {class_weight_dict}")

# ==============================================================================
# 🧠 6. MODEL ARCHITECTURE (V3: Deeper Bi-LSTM + Attention)
# ==============================================================================
print("\n🧠 Building the V3 Attention-Enhanced Bi-LSTM model...")

embedding_dim = 128   # V3: increased from 64 for richer embeddings
lstm_units = 128      # V3: increased from 64 for more capacity

inputs = Input(shape=(max_length,))

# Layer 1: Embedding
x = Embedding(vocab_size, embedding_dim, input_length=max_length)(inputs)
x = Dropout(0.3)(x)

# Layer 2: First Bidirectional LSTM
x = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
x = Dropout(0.3)(x)

# Layer 3: Second Bidirectional LSTM (V3: deeper)
x = Bidirectional(LSTM(lstm_units // 2, return_sequences=True))(x)
x = Dropout(0.3)(x)

# Layer 4: Attention Mechanism
attention_out = AttentionLayer()(x)

# Layer 5: Global Average Pooling (complementary feature)
avg_pool = GlobalAveragePooling1D()(x)

# Layer 6: Concatenate Attention + Average Pooling
x = Concatenate()([attention_out, avg_pool])

# Layer 7: Dense layers
x = Dense(128, activation='relu')(x)
x = Dropout(0.4)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(32, activation='relu')(x)

# Layer 8: Output (V3: 5 classes)
outputs = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=inputs, outputs=outputs)

# ==============================================================================
# ⚙️ 7. COMPILE & TRAIN
# ==============================================================================
model.compile(
    loss='sparse_categorical_crossentropy',
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=['accuracy']
)
model.summary(line_length=120)

# Callbacks for smart training
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_accuracy', patience=7, restore_best_weights=True
)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6
)

print("\n🚀 Starting V3 training...")
history = model.fit(
    X_train, y_train,
    epochs=40,              # V3: increased with EarlyStopping
    batch_size=32,
    validation_data=(X_test, y_test),
    class_weight=class_weight_dict,   # V3: balanced class weights
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# ==============================================================================
# 📈 8. EVALUATION
# ==============================================================================
print("\n📈 Evaluating on test set...")
y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
print("\n" + classification_report(y_test, y_pred, target_names=[
    "Happy (0)", "Sad/Stress (1)", "Critical (2)", "Out_Of_Context (3)", "Chitchat (4)"
]))

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"🎯 Test Accuracy: {test_acc:.4f}")

# ==============================================================================
# 💾 9. SAVE ARTIFACTS
# ==============================================================================
print("\n💾 Saving V3 model files...")
model.save("mental_health_model.h5")

with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Save model config for the bot to reference
config = {
    "vocab_size": vocab_size,
    "max_length": max_length,
    "num_classes": num_classes,
    "label_names": label_names
}
with open('model_config.pickle', 'wb') as handle:
    pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(f"\n🎉 V3 SUCCESS! Model trained with {test_acc:.2%} accuracy.")
print(f"   Saved: mental_health_model.h5, tokenizer.pickle, model_config.pickle")
print(f"   Classes: {num_classes} (Happy, Sad, Critical, OOC, Chitchat)")