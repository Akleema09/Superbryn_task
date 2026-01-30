# Setup Guide

## Step-by-Step Setup Instructions

### 1. Prerequisites

Install the following:
- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))
- Git ([Download](https://git-scm.com/))

### 2. Get API Keys

You'll need accounts and API keys for:

1. **LiveKit Cloud** (Free tier available)
   - Sign up at https://cloud.livekit.io
   - Create a project
   - Get your WebSocket URL, API Key, and API Secret

2. **Deepgram** (200 hours/month free)
   - Sign up at https://deepgram.com
   - Get your API key from the dashboard

3. **Cartesia** (Check current limits)
   - Sign up at https://cartesia.ai
   - Get your API key

4. **OpenAI** (Requires credit card)
   - Sign up at https://platform.openai.com
   - Add payment method
   - Get your API key

5. **Supabase** (Free tier available)
   - Sign up at https://supabase.com
   - Create a new project
   - Get your project URL and anon key

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
# Use your favorite text editor
```

### 4. Database Setup

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `backend/database/schema.sql`
4. Run the SQL script
5. Verify tables are created:
   - `users`
   - `appointments`

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# Set VITE_LIVEKIT_URL and VITE_TOKEN_API_URL
```

### 6. Running the Application

#### Terminal 1: Token Server
```bash
cd backend
python token_server.py
```

#### Terminal 2: LiveKit Agent
```bash
cd backend
python main.py dev
```

#### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

### 7. Testing

1. Open http://localhost:3000 in your browser
2. Click "Start Voice Call"
3. Allow microphone access when prompted
4. Test the following:
   - Say "I'd like to book an appointment"
   - Provide your phone number when asked
   - Book an appointment
   - Ask to see your appointments
   - End the conversation

## Troubleshooting

### "Failed to get LiveKit token"
- Make sure token server is running on port 8080
- Check `VITE_TOKEN_API_URL` in frontend `.env`
- Verify CORS is enabled on token server

### "Agent not responding"
- Check backend logs for errors
- Verify all API keys are correct
- Check LiveKit agent is connected

### "Database error"
- Verify Supabase credentials
- Check tables exist in database
- Verify RLS policies (if enabled)

### Microphone not working
- Check browser permissions
- Try HTTPS (required by some browsers)
- Check browser console for errors

## Next Steps

- Integrate Beyond Presence or Tavus for avatar
- Deploy to production (see DEPLOYMENT.md)
- Add cost tracking (optional bonus feature)
