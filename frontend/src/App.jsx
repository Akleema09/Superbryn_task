import React, { useState, useEffect } from 'react'
import VoiceCall from './components/VoiceCall'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🎙️ SuperBryn AI Voice Agent</h1>
        <p>Your intelligent appointment assistant</p>
      </header>
      <main className="app-main">
        <VoiceCall />
      </main>
    </div>
  )
}

export default App
