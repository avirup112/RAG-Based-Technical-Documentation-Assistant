from pymongo import MongoClient
from app.core.config import settings
from typing import List, Dict, Any
from app.core.llm import get_llm
from loguru import logger

class MemoryManager:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client["rag_assistant"]
        self.collection = self.db["sessions"]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieves chat history for a session.
        """
        session = self.collection.find_one({"session_id": session_id})
        if session and "chat_history" in session:
            return session["chat_history"]
        return []

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Returns all sessions ordered by most recent first.
        Each entry contains session_id and the first user message as a title.
        """
        sessions = self.collection.find(
            {},
            {"session_id": 1, "chat_history": 1, "_id": 0}
        ).sort("_id", -1).limit(30)

        result = []
        for s in sessions:
            history = s.get("chat_history", [])
            # Find the first user message to use as the session title
            title = next(
                (msg["content"][:60] for msg in history if msg.get("role") == "user"),
                "Empty session"
            )
            result.append({"session_id": s["session_id"], "title": title})
        return result

    def summarize_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Uses LLM to summarize older messages to save context space.
        """
        try:
            llm = get_llm(temperature=0.0)
            history_text = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            prompt = f"""
            Summarize the following conversation history concisely. 
            Focus on key technical details, technologies mentioned, and the overall context of what the user is trying to achieve.
            Keep it under 3 sentences.
            
            Conversation:
            {history_text}
            
            Summary:
            """
            res = llm.invoke(prompt)
            return res.content.strip()
        except Exception as e:
            logger.error(f"Failed to summarize history: {e}")
            return "Previous conversation context omitted."

    def save_interaction(self, session_id: str, question: str, answer: str):
        """
        Saves a question/answer pair to the session history.
        If history grows beyond 6 messages, compresses the older messages into a summary.
        """
        history = self.get_history(session_id)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        
        # If we have more than 6 messages (e.g. 1 summary + 6 actual messages)
        # we compress everything except the latest 4 messages (the last 2 Q&A pairs)
        if len(history) > 6:
            messages_to_summarize = history[:-4]
            recent_messages = history[-4:]
            
            logger.info(f"Summarizing {len(messages_to_summarize)} old messages for session {session_id}")
            summary_text = self.summarize_messages(messages_to_summarize)
            
            # The new history is just the system summary followed by the 4 most recent messages
            history = [{"role": "system", "content": f"Summary of previous conversation: {summary_text}"}] + recent_messages

        
        self.collection.update_one(
            {"session_id": session_id},
            {"$set": {"chat_history": history}},
            upsert=True
        )

    def save_feedback(self, session_id: str, question: str, answer: str, is_helpful: bool, comments: str = None):
        """
        Saves user feedback to the database.
        """
        feedback_collection = self.db["feedback"]
        feedback_collection.insert_one({
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "is_helpful": is_helpful,
            "comments": comments
        })
