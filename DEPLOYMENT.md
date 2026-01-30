# Deployment Guide

## Overview

This project consists of two main components:
1. **Backend**: Python LiveKit Agent + Token Server
2. **Frontend**: React Web Application

## Backend Deployment

### Option 1: Railway (Recommended)

1. Create a Railway account and new project
2. Connect your GitHub repository
3. Add environment variables (see `backend/.env.example`)
4. Deploy the agent service
5. Deploy token server as a separate service (port 8080)

### Option 2: Render

1. Create a new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py start`
5. Add environment variables
6. Create second service for token server

### Option 3: Fly.io

See `backend/DEPLOYMENT.md` for detailed Fly.io instructions.

## Frontend Deployment

### Option 1: Netlify (Recommended)

1. Connect GitHub repository to Netlify
2. Set build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Add environment variables:
   - `VITE_LIVEKIT_URL`: Your LiveKit URL
   - `VITE_TOKEN_API_URL`: Your backend token API URL
4. Deploy

### Option 2: Vercel

1. Connect GitHub repository to Vercel
2. Framework preset: Vite
3. Add environment variables
4. Deploy

## Environment Variables

### Backend

All variables from `backend/.env.example`:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `DEEPGRAM_API_KEY`
- `CARTESIA_API_KEY`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Frontend

- `VITE_LIVEKIT_URL`: LiveKit WebSocket URL
- `VITE_TOKEN_API_URL`: Backend token generation endpoint

## Database Setup

1. Create a Supabase project
2. Run the SQL schema from `backend/database/schema.sql`
3. Get your Supabase URL and anon key
4. Add to backend environment variables

## Post-Deployment Checklist

- [ ] Backend agent is running
- [ ] Token server is accessible
- [ ] Frontend can connect to LiveKit
- [ ] Database tables are created
- [ ] Environment variables are set
- [ ] Test end-to-end flow

## Troubleshooting

### Frontend can't connect to backend

- Check CORS settings on token server
- Verify `VITE_TOKEN_API_URL` is correct
- Check backend logs for errors

### Agent not responding

- Verify LiveKit credentials
- Check agent logs
- Verify Deepgram/Cartesia API keys

### Database errors

- Verify Supabase credentials
- Check table schema matches `schema.sql`
- Verify RLS policies allow access
