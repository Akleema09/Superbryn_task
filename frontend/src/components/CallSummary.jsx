import React from 'react'
import './CallSummary.css'

function CallSummary({ summary, onClose }) {
  const {
    summary_text,
    conversation_length,
    tool_calls_count,
    appointments_count,
    user_phone,
    timestamp,
    appointments = [],
  } = summary || {}

  return (
    <div className="call-summary-overlay">
      <div className="call-summary">
        <div className="call-summary-header">
          <h2>📋 Call Summary</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="call-summary-content">
          <div className="summary-section">
            <h3>Conversation Summary</h3>
            <div className="summary-text">
              {summary_text || 'No summary available'}
            </div>
          </div>

          <div className="stats-section">
            <div className="stat">
              <div className="stat-value">{conversation_length || 0}</div>
              <div className="stat-label">Exchanges</div>
            </div>
            <div className="stat">
              <div className="stat-value">{tool_calls_count || 0}</div>
              <div className="stat-label">Actions</div>
            </div>
            <div className="stat">
              <div className="stat-value">{appointments_count || 0}</div>
              <div className="stat-label">Appointments</div>
            </div>
          </div>

          {user_phone && (
            <div className="user-section">
              <h3>User Information</h3>
              <div className="user-info">
                <strong>Phone:</strong> {user_phone}
              </div>
            </div>
          )}

          {appointments && appointments.length > 0 && (
            <div className="appointments-section">
              <h3>Your Appointments</h3>
              <div className="appointments-list">
                {appointments.map((apt, index) => (
                  <div key={apt.id || index} className="appointment-item">
                    <div className="appointment-date-time">
                      <span className="date">{apt.date}</span>
                      <span className="time">{apt.time}</span>
                    </div>
                    <div className="appointment-details">
                      <div className="appointment-name">{apt.user_name}</div>
                      <div className={`appointment-status ${apt.status}`}>
                        {apt.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {timestamp && (
            <div className="timestamp-section">
              <small>Call ended: {new Date(timestamp).toLocaleString()}</small>
            </div>
          )}
        </div>

        <div className="call-summary-footer">
          <button className="done-button" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

export default CallSummary
