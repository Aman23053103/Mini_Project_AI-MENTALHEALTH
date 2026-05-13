"""Quick verification script for the trained model."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Layer

# Must redefine the custom layer before loading
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

# Load
model = tf.keras.models.load_model('mental_health_model.h5', custom_objects={'AttentionLayer': AttentionLayer})
tokenizer = pickle.load(open('tokenizer.pickle', 'rb'))
config = pickle.load(open('model_config.pickle', 'rb'))

print(f"Config: {config}")
label_names = {
    0: "Happy",
    1: "Sad/Stress",
    2: "Critical/Risk",
    3: "Out_Of_Context",
    4: "Chitchat"
}

# Test sentences
tests = [
    "i feel happy today",
    "life is lit bestie",
    "bahut stressed feel ho raha hai",
    "i want to die",
    "zindagi khatam karna chahta hu",
    "kya time hua hai",
    "bhai biryani khani hai",
    "tumhara naam kya hai",
    "feeling sad and lonely",
    "aaj ka match kaisa tha",
    "i am going to kill myself",
    "bhai kya chal raha hai",
    "feeling depressed and exhausted",
    "hello bhai",
    "ab nahi jhela jata i want to end it all",
]

seqs = tokenizer.texts_to_sequences([t.lower() for t in tests])
padded = pad_sequences(seqs, maxlen=config['max_length'], padding='post')
preds = model.predict(padded, verbose=0)

print("\n" + "="*70)
print(f"{'INPUT':<45} {'PREDICTION':<15} {'CONF'}")
print("="*70)
for t, p in zip(tests, preds):
    label = label_names[np.argmax(p)]
    conf = np.max(p)
    print(f"{t:<45} {label:<15} {conf:.1%}")
