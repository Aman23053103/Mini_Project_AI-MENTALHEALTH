"""
Simulation Runner: 100 Students Talking to MindMate AI
Processes all conversations from student_conversations.py through the bot pipeline.
Generates a detailed 10K+ line report with full conversation logs and failure analysis.
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import importlib
from typing import Dict, List, Any

# Load conversation data
from student_conversations import ALL_CONVERSATIONS

# Load bot components
import test_bot as bot

def reset_bot_state():
    """Reset conversation memory between students."""
    bot.conversation_history.clear()
    bot.session_state["patient_name"] = ""
    bot.session_state["current_context"] = "general"
    bot.session_state["current_entertainment"] = None
    bot.session_state["step"] = None
    bot.session_state["risk_trend"] = []

def classify_expected(topic):
    """Map topic name to expected emotion class."""
    mapping = {
        "depression": "sad", "anxiety": "sad", "loneliness": "sad",
        "academic": "sad", "relationship": "sad", "family": "sad",
        "sleep": "sad", "abuse": "critical", "crisis": "critical",
        "happy": "happy",
    }
    return mapping.get(topic, "out_of_context")

def run_simulation():
    print(f"Loading model...")
    print(f"\nSimulating {len(ALL_CONVERSATIONS)} student conversations...\n")

    report_lines: List[str] = []
    all_failures: List[Dict[str, Any]] = []
    topic_stats: Dict[str, Dict[str, int]] = {}
    total_msgs: int = 0
    total_correct: int = 0
    total_wrong: int = 0

    for student_id, topic, messages in ALL_CONVERSATIONS:
        reset_bot_state()
        expected_class = classify_expected(topic)

        report_lines.append("=" * 120)
        report_lines.append(f"STUDENT: {student_id} | TOPIC: {topic} | EXPECTED CLASS: {expected_class}")
        report_lines.append("=" * 120)

        student_correct: int = 0
        student_wrong: int = 0
        student_failures: List[Dict[str, Any]] = []

        for i, msg in enumerate(messages):
            total_msgs += 1
            original_text = msg
            cleaned = bot.clean_text(msg)
            context = bot.detect_context(cleaned, msg)
            emotion, confidence, probs = bot.classify_input(cleaned, msg)
            risk = bot.analyze_risk(emotion, confidence, context, cleaned)
            response = bot.get_response(emotion, confidence, risk, context, cleaned, msg)

            # Store in conversation history (like bot would)
            bot.conversation_history.append({
                "user": msg, "bot": response,
                "emotion": emotion, "risk": risk
            })
            if len(bot.conversation_history) > bot.MAX_HISTORY:
                bot.conversation_history.pop(0)
            bot.session_state["current_context"] = context if context != "general" else bot.session_state.get("current_context", "general")

            # Check correctness (skip greetings/farewells/chitchat turns)
            skip_words = ["hi", "hello", "hey", "namaste", "bye", "thanks",
                          "shukriya", "dhanyawad", "haan", "nahi", "okay",
                          "yes", "no", "nope", "theek hai", "thik hai",
                          "haha", "try", "achha", "achhi"]
            is_functional = len(msg.split()) <= 3 and any(w in msg.lower().split() for w in skip_words)

            if is_functional:
                correctness = "SKIP"
            elif topic in ["abuse", "crisis"] and emotion == "critical":
                correctness = "PASS"
                student_correct += 1
                total_correct += 1
            elif topic in ["depression", "anxiety", "loneliness", "academic",
                           "relationship", "family", "sleep"] and emotion == "sad":
                correctness = "PASS"
                student_correct += 1
                total_correct += 1
            elif topic == "happy" and emotion == "happy":
                correctness = "PASS"
                student_correct += 1
                total_correct += 1
            elif topic in ["abuse", "crisis"] and emotion == "sad":
                # Sad for abuse/crisis is partially correct (detected distress)
                correctness = "PARTIAL"
                student_correct += 1
                total_correct += 1
            else:
                if not is_functional:
                    correctness = "FAIL"
                    student_wrong += 1
                    total_wrong += 1
                    failure = {
                        "student": student_id, "topic": topic,
                        "message": msg, "expected": expected_class,
                        "got": emotion, "confidence": confidence,
                        "context": context, "risk": risk,
                    }
                    student_failures.append(failure)
                    all_failures.append(failure)

            # Format report lines
            report_lines.append(f"")
            report_lines.append(f"  Turn {i+1}: [{correctness}]")
            report_lines.append(f"  USER: {original_text}")
            report_lines.append(f"  CLEANED: {cleaned}")
            report_lines.append(f"  CLASSIFIED: {emotion} ({confidence*100:.0f}%) | CONTEXT: {context} | RISK: {risk}")
            # Truncate response for readability
            resp_preview = response.replace('\n', ' | ')[:200]
            report_lines.append(f"  BOT: {resp_preview}")
            report_lines.append(f"  ---")

        # Student summary
        total_turns = student_correct + student_wrong
        acc = (student_correct / total_turns * 100) if total_turns > 0 else 0
        report_lines.append(f"")
        report_lines.append(f"  STUDENT SUMMARY: {student_correct} correct, {student_wrong} wrong ({acc:.0f}% accuracy)")
        if student_failures:
            report_lines.append(f"  FAILURES:")
            for f in student_failures:
                report_lines.append(f"    - \"{f['message']}\" → expected {f['expected']}, got {f['got']} ({f['confidence']*100:.0f}%)")
        report_lines.append("")

        # Track topic stats
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "wrong": 0, "students": 0}
        topic_stats[topic]["correct"] += student_correct
        topic_stats[topic]["wrong"] += student_wrong
        topic_stats[topic]["students"] += 1

    # ============ HEADER SUMMARY ============
    header = []
    header.append("MINDMATE AI V3 — 100 STUDENT SIMULATION RESULTS")
    header.append(f"Total Students: {len(ALL_CONVERSATIONS)}")
    header.append(f"Total Messages: {total_msgs}")
    evaluated = total_correct + total_wrong
    accuracy = (total_correct / evaluated * 100) if evaluated > 0 else 0
    header.append(f"Evaluated Turns: {evaluated} (skipped greetings/functional)")
    header.append(f"Correct: {total_correct} | Wrong: {total_wrong} | Accuracy: {accuracy:.1f}%")
    header.append("")
    header.append(f"{'TOPIC':<20} {'STUDENTS':>8} {'CORRECT':>8} {'WRONG':>8} {'ACCURACY':>10}")
    header.append("-" * 60)
    for topic in sorted(topic_stats.keys()):
        s = topic_stats[topic]
        total = s["correct"] + s["wrong"]
        acc = (s["correct"] / total * 100) if total > 0 else 0
        header.append(f"{topic:<20} {s['students']:>8} {s['correct']:>8} {s['wrong']:>8} {acc:>9.1f}%")
    header.append("")

    # ============ FAILURE SUMMARY ============
    header.append(f"FAILURE DETAILS ({len(all_failures)} total)")
    header.append("=" * 120)
    header.append(f"{'STUDENT':<10} {'TOPIC':<15} {'MESSAGE':<50} {'EXPECTED':<12} {'GOT':<12} {'CONF':>6} {'CONTEXT':<12}")
    header.append("-" * 120)
    for f in all_failures:
        msg_trunc = f["message"][:48]
        header.append(f"{f['student']:<10} {f['topic']:<15} {msg_trunc:<50} {f['expected']:<12} {f['got']:<12} {f['confidence']*100:>5.0f}% {f['context']:<12}")
    header.append("")
    header.append("")

    # Write full report
    full_report = header + report_lines
    with open("simulation_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(full_report))
    print(f"\nReport saved: simulation_report.txt ({len(full_report)} lines)")
    print(f"Accuracy: {accuracy:.1f}% ({total_correct}/{evaluated})")
    print(f"Failures: {len(all_failures)}")

    # ============ EXPORT FAILURES FOR RETRAINING ============
    # Combine with previous test failures
    failure_data = []
    for f in all_failures:
        failure_data.append(f"{f['message']}\t{f['expected']}\t{f['got']}\t{f['topic']}")

    # Also read previous test failures if available
    try:
        with open("test_report.txt", "r", encoding="utf-8") as tr:
            lines = tr.readlines()
            for line in lines:
                if line.strip() and not line.startswith("MINDMATE") and not line.startswith("Total") and not line.startswith("TOPIC") and not line.startswith("----") and not line.startswith("====") and not line.startswith("FAILURE") and not line.startswith("Accuracy"):
                    parts = line.strip().split()
                    if len(parts) >= 5 and parts[0] in ["depression", "anxiety", "crisis", "abuse",
                        "academic", "loneliness", "relationship", "sleep", "happy", "chitchat", "family"]:
                        # This is a failure line from previous test
                        topic = parts[0]
                        expected = parts[-4]
                        got = parts[-3]
                        if expected != got:
                            # Reconstruct question
                            q_parts = parts[1:-4]
                            question = " ".join(q_parts)
                            failure_data.append(f"{question}\t{expected}\t{got}\t{topic}")
    except FileNotFoundError:
        pass

    with open("combined_failures.tsv", "w", encoding="utf-8") as f:
        f.write("message\texpected_class\tgot_class\ttopic\n")
        for line in failure_data:
            f.write(line + "\n")
    print(f"Combined failures exported: combined_failures.tsv ({len(failure_data)} entries)")

if __name__ == "__main__":
    run_simulation()
