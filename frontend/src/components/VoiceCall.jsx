import React, { useState, useEffect, useRef } from 'react'
import { Room, RoomEvent, DataPacket_Kind, RemoteParticipant, createLocalTracks } from 'livekit-client'
import AvatarDisplay from './AvatarDisplay'
import ToolCallDisplay from './ToolCallDisplay'
import CallSummary from './CallSummary'
import './VoiceCall.css'

const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL || 'wss://your-project.livekit.cloud'
const LIVEKIT_TOKEN = import.meta.env.VITE_LIVEKIT_TOKEN || ''

function VoiceCall() {
  const [room, setRoom] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [toolCalls, setToolCalls] = useState([])
  const [conversationSummary, setConversationSummary] = useState(null)
  const [error, setError] = useState(null)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  
  const audioRef = useRef(null)
  const roomRef = useRef(null)

  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect()
      }
    }
  }, [])

  const connectToRoom = async () => {
    if (isConnecting || isConnected) return

    setIsConnecting(true)
    setError(null)

    try {
      const roomName = `superbryn-${Date.now()}`
      const tokenResponse = await fetchToken(roomName)
      const token = tokenResponse.token || tokenResponse
      const url = tokenResponse.url || LIVEKIT_URL

      const newRoom = new Room({ adaptiveStream: true, dynacast: true })

      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to room')
        setIsConnected(true)
        setIsConnecting(false)
      })

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from room')
        setIsConnected(false)
        setRoom(null)
      })

      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        console.log('Participant connected:', participant.identity)
        console.log('Participant audioTracks:', participant.audioTracks)

        // Attach any already-published tracks for this participant
        try {
          participant.audioTracks.forEach((pub) => {
            const track = pub.track || pub.trackPublished || pub.trackSubscribed
            if (track && audioRef.current) {
              try { audioRef.current.muted = false; audioRef.current.volume = 1.0 } catch (e) {}
              try {
                track.attach(audioRef.current)
                console.log('Attached existing remote audio track to element for', participant.identity)
              } catch (e) {
                console.debug('attach failed for existing track', e)
              }
              audioRef.current.play().catch((e) => console.debug('Audio play suppressed:', e))
            }
          })
        } catch (e) {
          console.debug('Error attaching existing audio tracks', e)
        }

        // Subscribe handler for newly-published tracks
        participant.on('trackSubscribed', (track) => {
          try {
            console.log('trackSubscribed event:', { kind: track.kind, participant: participant.identity })
            if (track.kind === 'audio' && audioRef.current) {
              try { audioRef.current.muted = false; audioRef.current.volume = 1.0 } catch (e) {}
              track.attach(audioRef.current)
              console.log('Attached remote audio track to element for', participant.identity)
              audioRef.current.play().catch((e) => console.debug('Audio play suppressed:', e))
            }
          } catch (err) {
            console.debug('Error in trackSubscribed handler', err)
          }
        })
      })

      newRoom.on(RoomEvent.ParticipantDisconnected, (participant) => {
        console.log('Participant disconnected:', participant.identity)
      })

      newRoom.on(RoomEvent.DataReceived, (payload, participant, kind, topic) => {
        if (kind === DataPacket_Kind.RELIABLE) {
          try {
            const data = JSON.parse(new TextDecoder().decode(payload))
            handleToolCallEvent(data)
          } catch (e) {
            console.error('Error parsing data:', e)
          }
        }
      })

      // Connect to room
      await newRoom.connect(url, token)

      // Also attach any participants that were already in the room at connect time
      try {
        newRoom.participants.forEach((participant) => {
          console.log('Existing participant at connect:', participant.identity)
          participant.audioTracks.forEach((pub) => {
            const track = pub.track || pub.trackPublished || pub.trackSubscribed
            if (track && audioRef.current) {
              try { audioRef.current.muted = false; audioRef.current.volume = 1.0 } catch (e) {}
              try {
                track.attach(audioRef.current)
                console.log('Attached remote audio (existing) to element for', participant.identity)
              } catch (e) {
                console.debug('attach failed for existing participant track', e)
              }
              audioRef.current.play().catch((e) => console.debug('Audio play suppressed:', e))
            }
          })
        })
      } catch (e) {
        console.debug('Error attaching tracks after connect', e)
      }

      // publish local mic
      try {
        const localTracks = await createLocalTracks({ audio: true, video: false })
        if (localTracks && localTracks.length) {
          for (const t of localTracks) {
            try {
              await newRoom.localParticipant.publishTrack(t)
              console.log('Published local track', t.kind)
            } catch (e) {
              console.warn('Failed to publish local track:', e)
            }
          }
        }
      } catch (e) {
        console.warn('Could not get microphone permission or create local tracks:', e)
      }

      setRoom(newRoom)
      roomRef.current = newRoom
    } catch (err) {
      console.error('Error connecting to room:', err)
      setError(err.message || 'Failed to connect to voice agent')
      setIsConnecting(false)
    }
  }

  const fetchToken = async (roomName) => {
    // Call backend to generate a token
    const tokenUrl = import.meta.env.VITE_TOKEN_API_URL || 'http://localhost:8080/api/livekit-token'
    try {
      const response = await fetch(tokenUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roomName,
          participantName: 'user',
        }),
      })
      
      if (!response.ok) {
        throw new Error(`Token generation failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      return data
    } catch (err) {
      console.error('Error fetching token:', err)
      throw new Error('Failed to get LiveKit token. Make sure the token server is running.')
    }
  }

  const handleToolCallEvent = (data) => {
    const { type, data: eventData, timestamp } = data

    switch (type) {
      case 'user_speech':
        setIsListening(false)
        setIsSpeaking(true)
        setToolCalls(prev => [...prev, {
          id: Date.now(),
          type: 'user_speech',
          data: eventData,
          timestamp,
        }])
        break

      case 'function_call':
        setToolCalls(prev => [...prev, {
          id: Date.now(),
          type: 'function_call',
          data: eventData,
          timestamp,
        }])
        break

      case 'function_result':
        setToolCalls(prev => {
          const updated = [...prev]
          const lastCall = updated[updated.length - 1]
          if (lastCall && lastCall.type === 'function_call') {
            lastCall.result = eventData.result
          }
          return updated
        })
        setIsSpeaking(false)
        setIsListening(true)
        break

      case 'conversation_summary':
        setConversationSummary(eventData)
        setIsSpeaking(false)
        setIsListening(false)
        break

      default:
        console.log('Unknown event type:', type)
    }
  }

  const disconnect = async () => {
    if (room) {
      await room.disconnect()
      setRoom(null)
      setIsConnected(false)
      setToolCalls([])
      setConversationSummary(null)
    }
  }

  if (conversationSummary) {
    return (
      <CallSummary
        summary={conversationSummary}
        onClose={() => {
          setConversationSummary(null)
          disconnect()
        }}
      />
    )
  }

  return (
    <div className="voice-call">
      <div className="voice-call-container">
        {/* Avatar Display */}
        <div className="avatar-section">
          <AvatarDisplay
            isSpeaking={isSpeaking}
            isListening={isListening}
            isConnected={isConnected}
          />
        </div>

        {/* Connection Controls */}
        <div className="controls-section">
          {!isConnected && !isConnecting && (
            <button
              className="connect-button"
              onClick={connectToRoom}
            >
              Start Voice Call
            </button>
          )}

          {isConnecting && (
            <div className="connecting">
              <div className="spinner"></div>
              <p>Connecting to agent...</p>
            </div>
          )}

          {isConnected && (
            <button
              className="disconnect-button"
              onClick={disconnect}
            >
              End Call
            </button>
          )}

          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
              <p className="error-hint">
                Make sure LIVEKIT_URL and LIVEKIT_TOKEN are configured correctly.
                You may need to implement token generation on your backend.
              </p>
            </div>
          )}
        </div>

        {/* Tool Calls Display */}
        {toolCalls.length > 0 && (
          <div className="tool-calls-section">
            <h3>Activity</h3>
            <div className="tool-calls-list">
              {toolCalls.map((call) => (
                <ToolCallDisplay key={call.id} call={call} />
              ))}
            </div>
          </div>
        )}

        {/* Status Indicators */}
        {isConnected && (
          <div className="status-indicators">
            {isListening && (
              <div className="status-badge listening">
                🎤 Listening...
              </div>
            )}
            {isSpeaking && (
              <div className="status-badge speaking">
                🔊 Speaking...
              </div>
            )}
          </div>
        )}
      </div>

      {/* Hidden audio element for agent's voice (showing controls for debug) */}
      <audio ref={audioRef} autoPlay playsInline controls style={{display: 'block'}} />
    </div>
  )
}

export default VoiceCall
