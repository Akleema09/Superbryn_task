# SuperBryn AI Voice Agent - Backend

Backend implementation for the SuperBryn AI Voice Agent using LiveKit Agents.

## Features

- 🎙️ Real-time voice conversation with speech recognition (Deepgram) and text-to-speech (Cartesia)
- 🤖 AI-powered conversation using OpenAI GPT-4o
- 📅 Appointment management (book, retrieve, cancel, modify)
- 💾 Database integration with Supabase
- 📝 Automatic conversation summarization

## Setup

### Prerequisites

- Python 3.10+
- LiveKit Cloud account (free tier available)
- Deepgram API key (200 hours/month free)
- Cartesia API key
- OpenAI API key
- Supabase account (free tier available)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Set up Supabase database:
   - Create a new Supabase project
   - Run the SQL schema (see `database/schema.sql`)
   - Get your Supabase URL and anon key

5. Run the agent:
```bash
python main.py dev
```

## Database Schema

The backend requires the following Supabase tables:

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  phone_number TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Appointments Table
```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  phone_number TEXT NOT NULL,
  user_name TEXT NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  status TEXT DEFAULT 'confirmed',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Configuration

All configuration is done via environment variables in `.env`:

- `LIVEKIT_URL`: Your LiveKit Cloud WebSocket URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `DEEPGRAM_API_KEY`: Deepgram API key for speech-to-text
- `CARTESIA_API_KEY`: Cartesia API key for text-to-speech
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key

## Deployment

The backend can be deployed to any platform that supports Python (e.g., Railway, Render, Fly.io).

For LiveKit Cloud deployment, follow the LiveKit Agents deployment guide.

## API Endpoints

The agent runs as a LiveKit agent and connects via WebSocket. The frontend connects to LiveKit rooms where the agent is active.

## Tool Functions

The agent supports the following tool functions:

1. `identify_user` - Identify user by phone number
2. `fetch_slots` - Get available appointment slots
3. `book_appointment` - Book a new appointment
4. `retrieve_appointments` - Get user's appointments
5. `cancel_appointment` - Cancel an appointment
6. `modify_appointment` - Modify appointment date/time
7. `end_conversation` - End the conversation

## Known Limitations

- Avatar integration is handled on the frontend
- Tool call events are sent via LiveKit data channels
- Summary generation may take a few seconds for long conversations
