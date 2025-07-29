import React, { useState } from 'react';
import { useQuery, useMutation, gql } from '@apollo/client';
import Note from './components/Note';

// GraphQL Queries and Mutations
const GET_NOTES = gql`
  query GetNotes {
    notes {
      id
      content
      date
      important
    }
  }
`;

const ADD_NOTE = gql`
  mutation AddNote($content: String!, $important: Boolean) {
    addNote(content: $content, important: $important) {
      id
      content
      date
      important
    }
  }
`;

const TOGGLE_IMPORTANCE = gql`
  mutation ToggleImportance($id: String!) {
    toggleImportance(id: $id) {
      id
      content
      date
      important
    }
  }
`;

const App = () => {
  const [newNote, setNewNote] = useState('');
  const [showAll, setShowAll] = useState(true);

  // GraphQL Query Hook
  const { loading, error, data, refetch } = useQuery(GET_NOTES, {
    pollInterval: 5000, // Refresh every 5 seconds
  });

  // GraphQL Mutation Hooks
  const [addNote] = useMutation(ADD_NOTE, {
    refetchQueries: [{ query: GET_NOTES }],
    onCompleted: () => {
      setNewNote('');
    },
    onError: (error) => {
      console.error('Error adding note:', error);
    }
  });

  const [toggleImportance] = useMutation(TOGGLE_IMPORTANCE, {
    refetchQueries: [{ query: GET_NOTES }],
  });

  const handleAddNote = async (event) => {
    event.preventDefault();
    
    if (newNote.trim() === '') {
      alert('Please enter note content');
      return;
    }

    try {
      await addNote({
        variables: {
          content: newNote,
          important: Math.random() > 0.5, // Random importance like before
        }
      });
    } catch (err) {
      console.error('Failed to add note:', err);
    }
  };

  const handleNoteChange = (event) => {
    setNewNote(event.target.value);
  };

  const handleToggleImportance = async (id) => {
    try {
      await toggleImportance({
        variables: { id }
      });
    } catch (err) {
      console.error('Failed to toggle importance:', err);
    }
  };

  if (loading) return <div>Loading notes...</div>;
  if (error) return <div>Error loading notes: {error.message}</div>;

  const notes = data?.notes || [];
  const notesToShow = showAll ? notes : notes.filter(note => note.important);

  return (
    <div>
      <h1>GraphQL Notes</h1>
      <div>
        <button onClick={() => setShowAll(!showAll)}>
          Show {showAll ? 'important' : 'all'} notes
        </button>
        <button onClick={() => refetch()} style={{ marginLeft: '10px' }}>
          Refresh
        </button>
        <span style={{ marginLeft: '10px', color: '#666' }}>
          Total: {notes.length} notes
        </span>
      </div>
      <ul>
        {notesToShow.map(note => (
          <Note 
            key={note.id} 
            note={note} 
            toggleImportance={() => handleToggleImportance(note.id)}
          />
        ))}
      </ul>
      <form onSubmit={handleAddNote}>
        <input
          value={newNote}
          onChange={handleNoteChange}
          placeholder="Enter new note..."
        />
        <button type="submit">Save Note</button>
      </form>
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}>
        <p> GraphQL Endpoint: http://localhost:4000/graphql</p>
        <p> GraphiQL Interface: <a href="http://localhost:4000/graphql" target="_blank" rel="noopener noreferrer">Open GraphiQL</a></p>
      </div>
    </div>
  );
};

export default App;