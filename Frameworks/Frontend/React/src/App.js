import React, { useState, useEffect } from 'react'

import Note from './components/Note'

import axios from 'axios'

const App = () => {

  const [notes, setNotes] = useState([])

  const [newNote, setNewNote] = useState('')

  const [showAll, setShowAll] = useState(false)

  useEffect(() => {

    console.log('useEffect')

    axios
      .get('http://localhost:8000/notes')
      .then(response => {
        console.log('promise fulfilled')
        setNotes(response.data)
      })
  }, [])

  console.log('App', notes.length)

  const addNote = (event) => {

    event.preventDefault()

    const noteObject = {
      content: newNote,
      date: new Date().toISOString(),
      important: Math.random() > 0.5,
    }

    axios
    .post('http://localhost:8000/notes', noteObject)
    .then(response => {
      setNotes(notes.concat(response.data))
      setNewNote('')
    })
  }

  const handleNoteChange = (event) => {

    console.log(event.target.value)

    setNewNote(event.target.value)
  }

  const notesToShow = showAll ? notes : notes.filter(note => note.important)

  return (
    <div>
      <h1>Notes</h1>
      <div>
        <button onClick={() => setShowAll(!showAll)}>
          Show {showAll ? 'important' : 'all' }
        </button>
      </div>   
      <ul>
        {notesToShow.map(note => 
            <Note key={note.id} note={note} />
        )}
      </ul>
      <form onSubmit={addNote}>
        <input
          value={newNote}
          onChange={handleNoteChange}
        />
        <button type="submit">Save</button>
      </form>  
    </div>
  )
}

export default App