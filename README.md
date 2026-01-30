# SuperBryn AI Voice Agent

A web-based AI voice agent with visual avatar that can have natural conversations and book/retrieve appointments.

## 🎯 Features

- 🎙️ **Real-time Voice Conversation**: Speech recognition (Deepgram) and text-to-speech (Cartesia)
- 🤖 **AI-Powered**: Uses OpenAI GPT-4o for natural conversation
- 👤 **Visual Avatar**: Animated avatar synchronized with speech (placeholder - integrate Beyond Presence/Tavus)
- 📅 **Appointment Management**: Book, retrieve, cancel, and modify appointments
- 💾 **Database Integration**: Supabase for persistent storage
- 📝 **Call Summaries**: Automatic conversation summarization at end of call
- 🎨 **Modern UI**: Beautiful, responsive web interface

## 📁 Project Structure

```
Superbryn_task/
├── backend/          # Python LiveKit Agent
│   ├── agent.py      # Main agent implementation
│   ├── tools.py      # Tool definitions and execution
│   ├── database.py   # Supabase database operations
│   ├── summarizer.py # Conversation summarization
│   ├── main.py       # Entry point
│   └── token_server.py # Token generation server
│
└── frontend/         # React Web Application
    ├── src/
    │   ├── components/
    │   │   ├── VoiceCall.jsx      # Main call interface
    │   │   ├── AvatarDisplay.jsx  # Avatar component
    │   │   ├── ToolCallDisplay.jsx # Tool call visualization
    │   │   └── CallSummary.jsx    # Summary display
    │   └── App.jsx
    └── package.json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- LiveKit Cloud account
- Deepgram API key
- Cartesia API key
- OpenAI API key
- Supabase account

### Backend Setup

1. Navigate to backend directory:
```bash
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
   - Run the SQL schema from `database/schema.sql`
   - Get your Supabase URL and anon key

5. Start the token server (for frontend token generation):
```bash
python token_server.py
```

6. Run the agent (in a separate terminal):
```bash
python main.py dev
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your LiveKit configuration
```

4. Update `.env` to point to your token server:
```env
VITE_LIVEKIT_URL=wss://your-project.livekit.cloud
VITE_TOKEN_API_URL=http://localhost:8080/api/livekit-token
```

5. Start development server:
```bash
npm run dev
```

6. Open http://localhost:3000 in your browser

## 🔧 Configuration

### Backend Environment Variables

- `LIVEKIT_URL`: LiveKit Cloud WebSocket URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `DEEPGRAM_API_KEY`: Deepgram API key for STT
- `CARTESIA_API_KEY`: Cartesia API key for TTS
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key

### Frontend Environment Variables

- `VITE_LIVEKIT_URL`: LiveKit Cloud WebSocket URL
- `VITE_TOKEN_API_URL`: Backend token generation endpoint (default: http://localhost:8080/api/livekit-token)

## 📊 Database Schema

The backend requires two tables in Supabase:

1. **users**: Stores user phone numbers
2. **appointments**: Stores appointment records

See `backend/database/schema.sql` for the complete schema.

## 🛠️ Tool Functions

The agent supports the following tool functions:

1. **identify_user** - Identify user by phone number
2. **fetch_slots** - Get available appointment slots (hard-coded: 9 AM - 5 PM, hourly)
3. **book_appointment** - Book a new appointment
4. **retrieve_appointments** - Get user's appointments
5. **cancel_appointment** - Cancel an appointment
6. **modify_appointment** - Modify appointment date/time
7. **end_conversation** - End the conversation gracefully

## 🚢 Deployment

### Backend Deployment

The backend can be deployed to:
- Railway
- Render
- Fly.io
- Any platform supporting Python

Make sure to:
1. Set all environment variables
2. Run database migrations
3. Start both `main.py` (agent) and `token_server.py` (token generation)

### Frontend Deployment

The frontend can be deployed to:
- **Netlify**: Connect GitHub repo, set build command `npm run build`, output directory `dist`
- **Vercel**: Connect GitHub repo, set build command `npm run build`, output directory `dist`

Don't forget to set environment variables in the deployment platform.

## 🎨 Avatar Integration

The current implementation includes a placeholder avatar. To integrate Beyond Presence or Tavus:

1. **Beyond Presence**: Add their SDK/iframe component to `AvatarDisplay.jsx`
2. **Tavus**: Add their React component or iframe to `AvatarDisplay.jsx`

See `frontend/src/components/AvatarDisplay.jsx` for integration points.

## 📝 Known Limitations

1. **Avatar**: Currently using placeholder - needs Beyond Presence/Tavus integration
2. **Token Generation**: Frontend requires backend token server running
3. **Browser Compatibility**: Some browsers may require HTTPS for microphone access
4. **Cost Tracking**: Optional bonus feature not yet implemented

## 🧪 Testing

### End-to-End Testing

1. Start backend agent and token server
2. Start frontend development server
3. Open browser and click "Start Voice Call"
4. Test the following flows:
   - Identify user with phone number
   - Fetch available slots
   - Book an appointment
   - Retrieve appointments
   - Cancel an appointment
   - Modify an appointment
   - End conversation and view summary

## 📚 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## 🤝 Contributing

This is a task submission. For improvements or issues, please create GitHub issues.

## 📄 License

This project is a task submission for SuperBryn.
