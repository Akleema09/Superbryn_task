"""
Conversation summarizer for generating call summaries
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """Generates conversation summaries"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        self.client = OpenAI(api_key=api_key)
    
    async def generate_summary(
        self,
        conversation_history: List[Dict[str, Any]],
        tool_calls: List[Dict[str, Any]],
        user_phone: Optional[str],
        db,
    ) -> Dict[str, Any]:
        """Generate a comprehensive conversation summary"""
        try:
            # Get user's appointments if phone is available
            appointments = []
            if user_phone:
                appointments = await db.get_user_appointments(user_phone)
            
            # Format conversation history
            conversation_text = self._format_conversation(conversation_history)
            
            # Format tool calls
            tool_calls_text = self._format_tool_calls(tool_calls)
            
            # Format appointments
            appointments_text = self._format_appointments(appointments)
            
            # Generate summary using OpenAI
            prompt = f"""Summarize this conversation between a user and SuperBryn AI assistant.

Conversation:
{conversation_text}

Actions Taken:
{tool_calls_text}

User's Appointments:
{appointments_text}

Please provide a comprehensive summary that includes:
1. Main topics discussed
2. Actions taken (appointments booked, cancelled, modified, retrieved)
3. User preferences mentioned
4. Any important details or notes

Format the summary in a natural, conversational way that would be useful for the user to review."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear, concise conversation summaries."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            summary_text = response.choices[0].message.content
            
            return {
                "summary_text": summary_text,
                "conversation_length": len(conversation_history),
                "tool_calls_count": len(tool_calls),
                "appointments_count": len(appointments),
                "user_phone": user_phone,
                "timestamp": datetime.now().isoformat(),
                "appointments": appointments,
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback summary
            return {
                "summary_text": f"Thank you for using SuperBryn! We had a conversation with {len(conversation_history)} exchanges. {len(tool_calls)} actions were taken.",
                "conversation_length": len(conversation_history),
                "tool_calls_count": len(tool_calls),
                "appointments_count": 0,
                "user_phone": user_phone,
                "timestamp": datetime.now().isoformat(),
                "appointments": [],
            }
    
    def _format_conversation(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history as text"""
        lines = []
        for entry in history:
            role = entry.get("role", "unknown")
            text = entry.get("text", "")
            lines.append(f"{role.capitalize()}: {text}")
        return "\n".join(lines)
    
    def _format_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Format tool calls as text"""
        if not tool_calls:
            return "No actions taken."
        
        lines = []
        for call in tool_calls:
            name = call.get("name", "unknown")
            args = call.get("args", {})
            result = call.get("result", {})
            
            lines.append(f"- {name}: {args}")
            if result.get("success"):
                lines.append(f"  Result: {result.get('message', 'Success')}")
            else:
                lines.append(f"  Error: {result.get('error', 'Failed')}")
        
        return "\n".join(lines)
    
    def _format_appointments(self, appointments: List[Dict[str, Any]]) -> str:
        """Format appointments as text"""
        if not appointments:
            return "No appointments found."
        
        lines = []
        for apt in appointments:
            status = apt.get("status", "unknown")
            date = apt.get("date", "unknown")
            time = apt.get("time", "unknown")
            name = apt.get("user_name", "unknown")
            
            lines.append(f"- {name}: {date} at {time} ({status})")
        
        return "\n".join(lines)
