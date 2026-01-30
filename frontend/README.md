# SuperBryn AI Voice Agent - Frontend

React frontend for the SuperBryn AI Voice Agent using LiveKit Web SDK.

## Features

- 🎙️ Real-time voice conversation interface
- 👤 Visual avatar display (placeholder - integrate Beyond Presence/Tavus)
- 📊 Real-time tool call visualization
- 📋 Call summary display
- 🎨 Modern, responsive UI

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- LiveKit Cloud account

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
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

4. Start development server:
```bash
npm run dev
```

5. Build for production:
```bash
npm run build
```

## Configuration

### Environment Variables

- `VITE_LIVEKIT_URL`: Your LiveKit Cloud WebSocket URL
- `VITE_LIVEKIT_TOKEN`: LiveKit token (for development only)

**Important**: In production, you should implement token generation on your backend. The frontend should call your backend API to get a LiveKit token for each session.

### Token Generation

You'll need to implement a backend endpoint that generates LiveKit tokens. Example:

```javascript
// Backend endpoint (e.g., /api/livekit-token)
app.post('/api/livekit-token', async (req, res) => {
  const { roomName, participantName } = req.body;
  
  const token = await generateLiveKitToken({
    roomName,
    participantName,
    // ... other options
  });
  
  res.json({ token });
});
```

Then update `VoiceCall.jsx` to fetch the token:

```javascript
const fetchToken = async (roomName) => {
  const response = await fetch('/api/livekit-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roomName, participantName: 'user' }),
  });
  const { token } = await response.json();
  return token;
};
```

## Avatar Integration

The current implementation includes a placeholder avatar. To integrate Beyond Presence or Tavus:

1. **Beyond Presence**: Add their SDK/iframe component
2. **Tavus**: Add their React component or iframe

Example integration in `AvatarDisplay.jsx`:

```jsx
// Beyond Presence example
<BeyondPresenceAvatar
  state={avatarState}
  isSpeaking={isSpeaking}
  isListening={isListening}
/>

// Or Tavus example
<TavusAvatar
  videoUrl={avatarVideoUrl}
  isPlaying={isSpeaking}
/>
```

## Deployment

### Netlify

1. Build the project: `npm run build`
2. Deploy the `dist` folder to Netlify
3. Set environment variables in Netlify dashboard

### Vercel

1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables in Vercel dashboard

## Components

- **VoiceCall**: Main component managing LiveKit connection
- **AvatarDisplay**: Visual avatar component (placeholder)
- **ToolCallDisplay**: Displays tool calls and results
- **CallSummary**: Shows conversation summary at end of call

## Known Limitations

- Token generation needs to be implemented on backend
- Avatar integration is placeholder - needs Beyond Presence/Tavus integration
- Audio handling may need adjustment based on browser compatibility
