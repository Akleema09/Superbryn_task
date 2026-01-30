"""
Database manager for Supabase operations
"""
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for appointments"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
    async def get_or_create_user(self, phone_number: str) -> Dict[str, Any]:
        """Get or create a user by phone number"""
        try:
            # Check if user exists
            result = self.supabase.table("users").select("*").eq("phone_number", phone_number).execute()
            
            if result.data:
                return result.data[0]
            
            # Create new user
            new_user = {
                "phone_number": phone_number,
                "created_at": datetime.now().isoformat(),
            }
            
            result = self.supabase.table("users").insert(new_user).execute()
            return result.data[0] if result.data else new_user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            # Return a basic user dict even if DB fails
            return {"phone_number": phone_number, "id": phone_number}
    
    async def create_appointment(
        self,
        phone_number: str,
        user_name: str,
        date: str,
        time: str,
    ) -> Dict[str, Any]:
        """Create a new appointment"""
        try:
            appointment = {
                "phone_number": phone_number,
                "user_name": user_name,
                "date": date,
                "time": time,
                "status": "confirmed",
                "created_at": datetime.now().isoformat(),
            }
            
            result = self.supabase.table("appointments").insert(appointment).execute()
            
            if result.data:
                return result.data[0]
            return appointment
            
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            # Return a basic appointment dict even if DB fails
            return {
                "id": f"appt_{datetime.now().timestamp()}",
                "phone_number": phone_number,
                "user_name": user_name,
                "date": date,
                "time": time,
                "status": "confirmed",
            }
    
    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get an appointment by ID"""
        try:
            result = self.supabase.table("appointments").select("*").eq("id", appointment_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting appointment: {e}")
            return None
    
    async def get_appointment_by_datetime(self, date: str, time: str) -> Optional[Dict[str, Any]]:
        """Get an appointment by date and time (for double-booking check)"""
        try:
            result = (
                self.supabase.table("appointments")
                .select("*")
                .eq("date", date)
                .eq("time", time)
                .eq("status", "confirmed")
                .execute()
            )
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error checking appointment availability: {e}")
            return None
    
    async def get_user_appointments(self, phone_number: str) -> List[Dict[str, Any]]:
        """Get all appointments for a user"""
        try:
            result = (
                self.supabase.table("appointments")
                .select("*")
                .eq("phone_number", phone_number)
                .order("date", desc=False)
                .order("time", desc=False)
                .execute()
            )
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting user appointments: {e}")
            return []
    
    async def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """Cancel an appointment"""
        try:
            result = (
                self.supabase.table("appointments")
                .update({"status": "cancelled", "updated_at": datetime.now().isoformat()})
                .eq("id", appointment_id)
                .execute()
            )
            
            if result.data:
                return result.data[0]
            return {"id": appointment_id, "status": "cancelled"}
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {"id": appointment_id, "status": "cancelled"}
    
    async def modify_appointment(
        self,
        appointment_id: str,
        new_date: Optional[str] = None,
        new_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify an appointment"""
        try:
            updates = {"updated_at": datetime.now().isoformat()}
            
            if new_date:
                updates["date"] = new_date
            if new_time:
                updates["time"] = new_time
            
            result = (
                self.supabase.table("appointments")
                .update(updates)
                .eq("id", appointment_id)
                .execute()
            )
            
            if result.data:
                return result.data[0]
            
            # Fallback
            appointment = await self.get_appointment(appointment_id)
            if appointment:
                if new_date:
                    appointment["date"] = new_date
                if new_time:
                    appointment["time"] = new_time
                return appointment
            
            return {"id": appointment_id}
            
        except Exception as e:
            logger.error(f"Error modifying appointment: {e}")
            return {"id": appointment_id}
