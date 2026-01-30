"""
Tool definitions and execution logic for the voice agent.
Uses livekit.agents.llm.function_tool and find_function_tools for tool registration.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from livekit.agents.llm import function_tool, find_function_tools

logger = logging.getLogger(__name__)


class AppointmentTools:
    """Holds appointment tools for the LLM; use find_function_tools(instance) to get the tool list."""

    def __init__(self, tool_manager: "ToolManager", db, user_phone_ref: list):
        self._tm = tool_manager
        self._db = db
        self._user_phone_ref = user_phone_ref

    @function_tool(description="Ask for and store the user's phone number to identify them.")
    async def identify_user(self, phone_number: str) -> str:
        result = await self._tm.execute_tool(
            "identify_user", {"phone_number": phone_number}, self._db, self._user_phone_ref[0]
        )
        if result.get("success"):
            self._user_phone_ref[0] = result.get("phone_number")
        return str(result)

    @function_tool(description="Fetch available appointment slots (9 AM to 5 PM, hourly).")
    async def fetch_slots(self, date: Optional[str] = None) -> str:
        result = await self._tm.execute_tool(
            "fetch_slots", {"date": date} if date else {}, self._db, None
        )
        return str(result)

    @function_tool(
        description="Book an appointment. Requires user identified first. Prevents double-booking."
    )
    async def book_appointment(
        self, date: str, time: str, user_name: str, phone_number: str
    ) -> str:
        result = await self._tm.execute_tool(
            "book_appointment",
            {"date": date, "time": time, "user_name": user_name, "phone_number": phone_number},
            self._db,
            self._user_phone_ref[0],
        )
        return str(result)

    @function_tool(description="Retrieve all appointments for the identified user.")
    async def retrieve_appointments(self, phone_number: str) -> str:
        result = await self._tm.execute_tool(
            "retrieve_appointments", {"phone_number": phone_number}, self._db, None
        )
        return str(result)

    @function_tool(description="Cancel an existing appointment.")
    async def cancel_appointment(self, appointment_id: str, phone_number: str) -> str:
        result = await self._tm.execute_tool(
            "cancel_appointment",
            {"appointment_id": appointment_id, "phone_number": phone_number},
            self._db,
            None,
        )
        return str(result)

    @function_tool(description="Modify an existing appointment's date or time.")
    async def modify_appointment(
        self,
        appointment_id: str,
        phone_number: str,
        new_date: Optional[str] = None,
        new_time: Optional[str] = None,
    ) -> str:
        args = {"appointment_id": appointment_id, "phone_number": phone_number}
        if new_date is not None:
            args["new_date"] = new_date
        if new_time is not None:
            args["new_time"] = new_time
        result = await self._tm.execute_tool("modify_appointment", args, self._db, None)
        return str(result)

    @function_tool(
        description="End the conversation gracefully when user says goodbye or is done."
    )
    async def end_conversation(self) -> str:
        result = await self._tm.execute_tool("end_conversation", {}, self._db, None)
        return str(result)


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Return raw OpenAI-style function schemas for all tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "identify_user",
                "description": "Ask for and store the user's phone number to identify them. Use this when you need to identify the user before booking, retrieving, canceling, or modifying appointments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "The user's phone number (e.g., '+1234567890' or '1234567890')",
                        },
                    },
                    "required": ["phone_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_slots",
                "description": "Fetch available appointment slots. Returns hard-coded available slots (every day from 9 AM to 5 PM in hourly intervals).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date to check slots for (YYYY-MM-DD format). If not provided, defaults to today.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Book an appointment for the user. Requires user to be identified first. Prevents double-booking.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Appointment date in YYYY-MM-DD format"},
                        "time": {"type": "string", "description": "Appointment time in HH:MM format (24-hour)"},
                        "user_name": {"type": "string", "description": "Name of the user booking the appointment"},
                        "phone_number": {"type": "string", "description": "Phone number of the user (should match identified user)"},
                    },
                    "required": ["date", "time", "user_name", "phone_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "retrieve_appointments",
                "description": "Retrieve all appointments for the identified user. Requires user to be identified first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string", "description": "Phone number of the user to retrieve appointments for"},
                    },
                    "required": ["phone_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment. Requires user to be identified first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "description": "The ID of the appointment to cancel"},
                        "phone_number": {"type": "string", "description": "Phone number of the user (for verification)"},
                    },
                    "required": ["appointment_id", "phone_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "modify_appointment",
                "description": "Modify an existing appointment's date or time. Requires user to be identified first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {"type": "string", "description": "The ID of the appointment to modify"},
                        "new_date": {"type": "string", "description": "New appointment date in YYYY-MM-DD format (optional)"},
                        "new_time": {"type": "string", "description": "New appointment time in HH:MM format (24-hour) (optional)"},
                        "phone_number": {"type": "string", "description": "Phone number of the user (for verification)"},
                    },
                    "required": ["appointment_id", "phone_number"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "end_conversation",
                "description": "End the conversation gracefully. Use this when the user says goodbye, thanks, or indicates they're done.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    ]


class ToolManager:
    """Manages tool execution logic."""

    async def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        db,
        current_user_phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        logger.info(f"Executing tool: {tool_name} with args: {args}")

        try:
            if tool_name == "identify_user":
                return await self._identify_user(args, db)
            elif tool_name == "fetch_slots":
                return await self._fetch_slots(args)
            elif tool_name == "book_appointment":
                return await self._book_appointment(args, db, current_user_phone)
            elif tool_name == "retrieve_appointments":
                return await self._retrieve_appointments(args, db)
            elif tool_name == "cancel_appointment":
                return await self._cancel_appointment(args, db)
            elif tool_name == "modify_appointment":
                return await self._modify_appointment(args, db)
            elif tool_name == "end_conversation":
                return {"success": True, "message": "Conversation ended"}
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}

    async def _identify_user(self, args: Dict[str, Any], db) -> Dict[str, Any]:
        """Identify user by phone number."""
        phone_number = args.get("phone_number", "").strip()
        if not phone_number:
            return {"success": False, "error": "Phone number is required"}
        phone_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        await db.get_or_create_user(phone_number)
        return {"success": True, "phone_number": phone_number, "message": f"User identified: {phone_number}"}

    async def _fetch_slots(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch available appointment slots."""
        date_str = args.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        else:
            target_date = datetime.now().date()
        slots = [{"date": target_date.isoformat(), "time": f"{h:02d}:00", "available": True} for h in range(9, 17)]
        return {"success": True, "date": target_date.isoformat(), "slots": slots, "message": f"Found {len(slots)} available slots on {target_date.isoformat()}"}

    async def _book_appointment(
        self, args: Dict[str, Any], db, current_user_phone: Optional[str],
    ) -> Dict[str, Any]:
        """Book an appointment."""
        date_str = args.get("date")
        time_str = args.get("time")
        user_name = args.get("user_name", "").strip()
        phone_number = args.get("phone_number", "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if current_user_phone and phone_number != current_user_phone:
            return {"success": False, "error": "Phone number mismatch. Please identify yourself first."}
        if not phone_number:
            phone_number = current_user_phone
        if not phone_number:
            return {"success": False, "error": "User must be identified first. Please provide your phone number."}
        try:
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"success": False, "error": "Invalid date or time format"}
        existing = await db.get_appointment_by_datetime(date_str, time_str)
        if existing:
            return {"success": False, "error": f"Slot {date_str} {time_str} is already booked"}
        appointment = await db.create_appointment(phone_number=phone_number, user_name=user_name, date=date_str, time=time_str)
        return {"success": True, "appointment": appointment, "message": f"Appointment booked successfully for {user_name} on {date_str} at {time_str}"}

    async def _retrieve_appointments(self, args: Dict[str, Any], db) -> Dict[str, Any]:
        """Retrieve user's appointments."""
        phone_number = args.get("phone_number", "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone_number:
            return {"success": False, "error": "Phone number is required"}
        appointments = await db.get_user_appointments(phone_number)
        return {"success": True, "appointments": appointments, "count": len(appointments), "message": f"Found {len(appointments)} appointment(s)"}

    async def _cancel_appointment(self, args: Dict[str, Any], db) -> Dict[str, Any]:
        """Cancel an appointment."""
        appointment_id = args.get("appointment_id")
        phone_number = args.get("phone_number", "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not appointment_id:
            return {"success": False, "error": "Appointment ID is required"}
        appointment = await db.get_appointment(appointment_id)
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        if appointment.get("phone_number") != phone_number:
            return {"success": False, "error": "You don't have permission to cancel this appointment"}
        await db.cancel_appointment(appointment_id)
        return {"success": True, "message": f"Appointment {appointment_id} cancelled successfully"}

    async def _modify_appointment(self, args: Dict[str, Any], db) -> Dict[str, Any]:
        """Modify an appointment."""
        appointment_id = args.get("appointment_id")
        new_date = args.get("new_date")
        new_time = args.get("new_time")
        phone_number = args.get("phone_number", "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not appointment_id:
            return {"success": False, "error": "Appointment ID is required"}
        if not new_date and not new_time:
            return {"success": False, "error": "At least one of new_date or new_time must be provided"}
        appointment = await db.get_appointment(appointment_id)
        if not appointment:
            return {"success": False, "error": "Appointment not found"}
        if appointment.get("phone_number") != phone_number:
            return {"success": False, "error": "You don't have permission to modify this appointment"}
        if new_date and new_time:
            existing = await db.get_appointment_by_datetime(new_date, new_time)
            if existing and existing.get("id") != appointment_id:
                return {"success": False, "error": f"Slot {new_date} {new_time} is already booked"}
        result = await db.modify_appointment(appointment_id=appointment_id, new_date=new_date, new_time=new_time)
        return {"success": True, "appointment": result, "message": f"Appointment {appointment_id} modified successfully"}
