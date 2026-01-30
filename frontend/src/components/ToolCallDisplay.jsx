import React from 'react'
import './ToolCallDisplay.css'

function ToolCallDisplay({ call }) {
  const { type, data, timestamp, result } = call

  const getIcon = () => {
    switch (type) {
      case 'user_speech':
        return '🎤'
      case 'function_call':
        return '⚙️'
      default:
        return '📝'
    }
  }

  const getTitle = () => {
    switch (type) {
      case 'user_speech':
        return 'You said'
      case 'function_call':
        return `Action: ${data.name || 'Unknown'}`
      default:
        return 'Event'
    }
  }

  const getContent = () => {
    switch (type) {
      case 'user_speech':
        return data.text || ''
      case 'function_call':
        return (
          <div className="function-call-details">
            <div className="function-name">{data.name}</div>
            {data.args && Object.keys(data.args).length > 0 && (
              <div className="function-args">
                <strong>Parameters:</strong>
                <pre>{JSON.stringify(data.args, null, 2)}</pre>
              </div>
            )}
            {result && (
              <div className={`function-result ${result.success ? 'success' : 'error'}`}>
                <strong>{result.success ? '✓ Success' : '✗ Error'}:</strong>
                <div>{result.message || result.error || JSON.stringify(result)}</div>
              </div>
            )}
          </div>
        )
      default:
        return JSON.stringify(data, null, 2)
    }
  }

  return (
    <div className={`tool-call ${type}`}>
      <div className="tool-call-header">
        <span className="tool-call-icon">{getIcon()}</span>
        <span className="tool-call-title">{getTitle()}</span>
        <span className="tool-call-time">
          {timestamp ? new Date(timestamp).toLocaleTimeString() : ''}
        </span>
      </div>
      <div className="tool-call-content">
        {getContent()}
      </div>
    </div>
  )
}

export default ToolCallDisplay
