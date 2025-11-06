"""
AI Conversation Manager με Memory και Logging
Αποθηκεύει όλες τις συνομιλίες, AI calls και ratings για dataset building
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

CONV_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations.db")

def init_conversation_db():
    """Δημιουργία πίνακα συνομιλιών και AI logs"""
    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    # Conversation history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            ai_response TEXT,
            ai_action TEXT,
            timestamp TEXT,
            rating INTEGER DEFAULT NULL,
            feedback TEXT DEFAULT NULL
        )
    """)

    # AI API calls logging table (για cost tracking)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            cost_usd REAL,
            latency_ms INTEGER,
            timestamp TEXT,
            success BOOLEAN,
            error_message TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()

def get_session_id() -> str:
    """Δημιουργία ή ανάκτηση session ID (για την τρέχουσα συνεδρία)"""
    # Για απλότητα, χρησιμοποιούμε ημερομηνία ως session
    return datetime.now().strftime("%Y-%m-%d")

def get_conversation_history(session_id: str = None, limit: int = 10) -> List[Dict]:
    """
    Ανάκτηση των τελευταίων N συνομιλιών για context

    Args:
        session_id: Το session ID (None = σημερινό)
        limit: Πόσα μηνύματα να επιστρέψει

    Returns:
        List με {role, content} για OpenAI format
    """
    init_conversation_db()

    if session_id is None:
        session_id = get_session_id()

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_message, ai_response
        FROM conversations
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, limit))

    rows = cur.fetchall()
    conn.close()

    # Αντιστροφή (πιο παλιά πρώτα) και μετατροπή σε OpenAI format
    history = []
    for user_msg, ai_msg in reversed(rows):
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": ai_msg})

    return history

def save_conversation(
    user_message: str,
    ai_response: str,
    ai_action: str = None,
    session_id: str = None
) -> int:
    """
    Αποθήκευση συνομιλίας

    Returns:
        conversation_id
    """
    init_conversation_db()

    if session_id is None:
        session_id = get_session_id()

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO conversations (session_id, user_message, ai_response, ai_action, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_message, ai_response, ai_action, datetime.now().isoformat()))

    conv_id = cur.lastrowid
    conn.commit()
    conn.close()

    return conv_id

def log_ai_api_call(
    conversation_id: int,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    success: bool = True,
    error_message: str = None
):
    """Log AI API call για cost tracking και analytics"""
    init_conversation_db()

    # Cost calculation (GPT-4o-mini rates)
    # Input: $0.150 / 1M tokens
    # Output: $0.600 / 1M tokens
    cost_usd = (prompt_tokens * 0.150 / 1_000_000) + (completion_tokens * 0.600 / 1_000_000)
    total_tokens = prompt_tokens + completion_tokens

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ai_api_logs
        (conversation_id, model, prompt_tokens, completion_tokens, total_tokens,
         cost_usd, latency_ms, timestamp, success, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (conversation_id, model, prompt_tokens, completion_tokens, total_tokens,
          cost_usd, latency_ms, datetime.now().isoformat(), success, error_message))

    conn.commit()
    conn.close()

def rate_conversation(conversation_id: int, rating: int, feedback: str = None):
    """Προσθήκη rating σε συνομιλία (1-5 stars)"""
    init_conversation_db()

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    cur.execute("""
        UPDATE conversations
        SET rating = ?, feedback = ?
        WHERE id = ?
    """, (rating, feedback, conversation_id))

    conn.commit()
    conn.close()

def get_dataset_export(min_rating: int = None) -> List[Dict]:
    """
    Export συνομιλιών για fine-tuning dataset

    Args:
        min_rating: Μόνο conversations με rating >= αυτό

    Returns:
        List με OpenAI fine-tuning format
    """
    init_conversation_db()

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    query = "SELECT user_message, ai_response, rating FROM conversations"
    params = []

    if min_rating is not None:
        query += " WHERE rating >= ?"
        params.append(min_rating)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    dataset = []
    for user_msg, ai_msg, rating in rows:
        dataset.append({
            "messages": [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": ai_msg}
            ],
            "rating": rating
        })

    return dataset

def get_analytics() -> Dict:
    """Επιστρέφει analytics για AI usage"""
    init_conversation_db()

    conn = sqlite3.connect(CONV_DB)
    cur = conn.cursor()

    # Total conversations
    cur.execute("SELECT COUNT(*) FROM conversations")
    total_convs = cur.fetchone()[0]

    # Total API calls και cost
    cur.execute("""
        SELECT
            COUNT(*) as total_calls,
            SUM(total_tokens) as total_tokens,
            SUM(cost_usd) as total_cost,
            AVG(latency_ms) as avg_latency
        FROM ai_api_logs
    """)
    api_stats = cur.fetchone()

    # Rating distribution
    cur.execute("""
        SELECT rating, COUNT(*)
        FROM conversations
        WHERE rating IS NOT NULL
        GROUP BY rating
    """)
    ratings = dict(cur.fetchall())

    conn.close()

    return {
        "total_conversations": total_convs,
        "total_api_calls": api_stats[0] or 0,
        "total_tokens": api_stats[1] or 0,
        "total_cost_usd": round(api_stats[2] or 0, 4),
        "avg_latency_ms": round(api_stats[3] or 0, 2),
        "rating_distribution": ratings
    }
