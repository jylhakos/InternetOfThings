import React from 'react';

const Note = ({ note, toggleImportance }) => {
  const label = note.important ? 'make not important' : 'make important';

  return (
    <li style={{ 
      padding: '8px', 
      margin: '4px 0', 
      border: '1px solid #ddd', 
      borderRadius: '4px',
      backgroundColor: note.important ? '#f0f8ff' : '#f9f9f9'
    }}>
      <div>
        <strong>{note.content}</strong>
        {note.important && <span style={{ color: 'red', marginLeft: '8px' }}>★</span>}
      </div>
      <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
        Created: {new Date(note.date).toLocaleString()}
      </div>
      {toggleImportance && (
        <button 
          onClick={toggleImportance}
          style={{ 
            marginTop: '4px', 
            fontSize: '11px',
            padding: '2px 6px',
            backgroundColor: note.important ? '#ffd700' : '#e0e0e0',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer'
          }}
        >
          {label}
        </button>
      )}
    </li>
  );
};

export default Note;