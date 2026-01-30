# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] All API keys ready (LiveKit, Deepgram, Cartesia, OpenAI, Supabase)

## 1. Backend Setup (2 minutes)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
```

## 2. Database Setup (1 minute)

1. Go to Supabase SQL Editor
2. Copy/paste `backend/database/schema.sql`
3. Run it
4. Verify tables created

## 3. Frontend Setup (1 minute)

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env - set VITE_LIVEKIT_URL and VITE_TOKEN_API_URL
```

## 4. Run Everything (1 minute)

**Terminal 1** (Token Server):
```bash
cd backend
python token_server.py
```

**Terminal 2** (Agent):
```bash
cd backend
python main.py dev
```

**Terminal 3** (Frontend):
```bash
cd frontend
npm run dev
```

## 5. Test It!

1. Open http://localhost:3000
2. Click "Start Voice Call"
3. Allow microphone access
4. Say: "I'd like to book an appointment"
5. Follow the conversation!

## Troubleshooting

**Can't connect?**
- Check token server is running on port 8080
- Verify all API keys in `.env`
- Check browser console for errors

**Agent not responding?**
- Check backend logs
- Verify LiveKit credentials
- Check Deepgram/Cartesia keys

**Database errors?**
- Verify Supabase credentials
- Check tables exist
- Verify RLS policies

## Next Steps

- See `SETUP.md` for detailed instructions
- See `DEPLOYMENT.md` for production deployment
- See `KNOWN_LIMITATIONS.md` for known issues
