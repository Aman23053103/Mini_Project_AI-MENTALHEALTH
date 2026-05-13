"""
Comprehensive test runner for MindMate AI V3.
Runs 1000+ questions through the full bot pipeline and generates a report.
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys
import re
import json
import tensorflow as tf
import numpy as np
import pickle
from typing import Dict, List, Any
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Layer
from test_questions import ALL_QUESTIONS

# === Load model ===
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
        return tf.keras.backend.sum(x * a, axis=1)

print("Loading model...")
model = tf.keras.models.load_model('mental_health_model.h5', custom_objects={'AttentionLayer': AttentionLayer})
tokenizer = pickle.load(open('tokenizer.pickle', 'rb'))
config = pickle.load(open('model_config.pickle', 'rb'))
LABEL_MAP = {0: "happy", 1: "sad", 2: "critical", 3: "out_of_context", 4: "chitchat"}
MAX_LENGTH = config['max_length']

# === Import bot functions from test_bot ===
import test_bot as bot

# === Run all tests ===
print(f"\nRunning {len(ALL_QUESTIONS)} tests across all topics...\n")

total_tests: int = 0
passed_tests: int = 0
failed_tests: int = 0
by_topic: Dict[str, Dict[str, int]] = {}
failures_list: List[Dict[str, Any]] = []

for topic, question, expected in ALL_QUESTIONS:
    total_tests += 1
    
    # Initialize topic stats
    if topic not in by_topic:
        by_topic[topic] = {"total": 0, "passed": 0, "failed": 0}
    by_topic[topic]["total"] += 1
    
    # Run through pipeline
    cleaned = bot.clean_text(question)
    emotion, confidence, probs = bot.classify_input(cleaned, question)
    context = bot.detect_context(cleaned, question)
    
    # Check classification (V3: chitchat and out_of_context are both acceptable for OOC questions)
    if expected == "out_of_context":
        passed = emotion in ["out_of_context", "chitchat"]
    else:
        passed = (emotion == expected)
    
    if passed:
        passed_tests += 1
        by_topic[topic]["passed"] += 1
    else:
        failed_tests += 1
        by_topic[topic]["failed"] += 1
        failures_list.append({
            "topic": topic,
            "question": question,
            "expected": expected,
            "got": emotion,
            "confidence": f"{confidence:.0%}",
            "context": context,
        })

# === Print Summary ===
print("=" * 100)
print(f"  MINDMATE AI V3 — COMPREHENSIVE TEST RESULTS")  
print(f"  Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}")
print(f"  Accuracy: {passed_tests/total_tests:.1%}" if total_tests > 0 else "  Accuracy: 0.0%")
print("=" * 100)

print(f"\n{'TOPIC':<20} {'TOTAL':>8} {'PASS':>8} {'FAIL':>8} {'ACCURACY':>10}")
print("-" * 60)
for topic in sorted(by_topic.keys()):
    stats = by_topic[topic]
    acc = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
    marker = "✅" if stats["failed"] == 0 else ("⚠️" if acc >= 0.8 else "❌")
    print(f"{marker} {topic:<18} {stats['total']:>6} {stats['passed']:>8} {stats['failed']:>8} {acc:>9.1%}")

# === Print Failures ===
if failures_list:
    print(f"\n{'=' * 100}")
    print(f"  FAILURES ({len(failures_list)} total)")
    print(f"{'=' * 100}")
    print(f"{'TOPIC':<15} {'QUESTION':<50} {'EXPECTED':<15} {'GOT':<15} {'CONF'}")
    print("-" * 100)
    for f in failures_list:
        q_short = f["question"][:48] if len(f["question"]) > 48 else f["question"]
        print(f"{f['topic']:<15} {q_short:<50} {f['expected']:<15} {f['got']:<15} {f['confidence']}")

# === Save report to file ===
report_file = "test_report.txt"
with open(report_file, "w", encoding="utf-8") as rf:
    rf.write(f"MINDMATE AI V3 — COMPREHENSIVE TEST RESULTS\n")
    rf.write(f"Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}\n")
    rf.write(f"Accuracy: {passed_tests/total_tests:.1%}\n\n" if total_tests > 0 else "Accuracy: 0.0%\n\n")
    
    rf.write(f"{'TOPIC':<20} {'TOTAL':>8} {'PASS':>8} {'FAIL':>8} {'ACCURACY':>10}\n")
    rf.write("-" * 60 + "\n")
    for topic in sorted(by_topic.keys()):
        stats = by_topic[topic]
        acc = stats["passed"] / stats["total"] if stats["total"] > 0 else 0
        rf.write(f"{topic:<20} {stats['total']:>6} {stats['passed']:>8} {stats['failed']:>8} {acc:>9.1%}\n")
    
    if failures_list:
        rf.write(f"\n\nFAILURES ({len(failures_list)} total)\n")
        rf.write("=" * 120 + "\n")
        rf.write(f"{'TOPIC':<15} {'QUESTION':<55} {'EXPECTED':<15} {'GOT':<15} {'CONF':<8} {'CONTEXT'}\n")
        rf.write("-" * 120 + "\n")
        for f in failures_list:
            rf.write(f"{f['topic']:<15} {f['question']:<55} {f['expected']:<15} {f['got']:<15} {f['confidence']:<8} {f['context']}\n")

print(f"\n📄 Full report saved to: {report_file}")
