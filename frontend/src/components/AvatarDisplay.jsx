import React, { useEffect, useState } from 'react'
import './AvatarDisplay.css'

function AvatarDisplay({ isSpeaking, isListening, isConnected }) {
  const [avatarState, setAvatarState] = useState('idle')

  useEffect(() => {
    if (isSpeaking) {
      setAvatarState('speaking')
    } else if (isListening) {
      setAvatarState('listening')
    } else if (isConnected) {
      setAvatarState('ready')
    } else {
      setAvatarState('idle')
    }
  }, [isSpeaking, isListening, isConnected])

  // For production, integrate with Beyond Presence or Tavus here
  // This is a placeholder avatar component
  const renderAvatar = () => {
    switch (avatarState) {
      case 'speaking':
        return (
          <div className="avatar speaking">
            <div className="avatar-face">
              <div className="avatar-eyes">
                <div className="eye left"></div>
                <div className="eye right"></div>
              </div>
              <div className="avatar-mouth speaking-mouth"></div>
            </div>
            <div className="sound-waves">
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
            </div>
          </div>
        )
      case 'listening':
        return (
          <div className="avatar listening">
            <div className="avatar-face">
              <div className="avatar-eyes">
                <div className="eye left"></div>
                <div className="eye right"></div>
              </div>
              <div className="avatar-mouth listening-mouth"></div>
            </div>
            <div className="listening-indicator">
              <div className="pulse-ring"></div>
              <div className="pulse-ring"></div>
              <div className="pulse-ring"></div>
            </div>
          </div>
        )
      case 'ready':
        return (
          <div className="avatar ready">
            <div className="avatar-face">
              <div className="avatar-eyes">
                <div className="eye left"></div>
                <div className="eye right"></div>
              </div>
              <div className="avatar-mouth"></div>
            </div>
            <p className="avatar-status">Ready to talk</p>
          </div>
        )
      default:
        return (
          <div className="avatar idle">
            <div className="avatar-face">
              <div className="avatar-eyes">
                <div className="eye left"></div>
                <div className="eye right"></div>
              </div>
              <div className="avatar-mouth"></div>
            </div>
            <p className="avatar-status">Click to start</p>
          </div>
        )
    }
  }

  return (
    <div className="avatar-display">
      {renderAvatar()}
      {/* 
        TODO: Integrate Beyond Presence or Tavus avatar here
        Example:
        <iframe 
          src={`https://your-avatar-url.com?state=${avatarState}`}
          className="avatar-iframe"
        />
      */}
    </div>
  )
}

export default AvatarDisplay
