import React, { useState, useEffect } from 'react'

import Note from './components/Note'

import Notification from './components/Notification'

import LoginForm from './components/LoginForm'

import NoteForm from './components/NoteForm'

import Togglable from './components/Togglable'

import Footer from './components/Footer'

import noteService from './services/notes'

import loginService from './services/login' 

const App = () => {

  const [notes, setNotes] = useState([])

  const [newNote, setNewNote] = useState('')


  const [showAll, setShowAll] = useState(false)

  const [errorMessage, setErrorMessage] = useState(null)

  const [loginVisible, setLoginVisible] = useState(false)

  const [username, setUsername] = useState('anonymous') 

  const [password, setPassword] = useState('12345') 

  const [user, setUser] = useState(null)

  useEffect(() => {

    noteService
      .getAll()
      .then(initialNotes => {
      setNotes(initialNotes)
    })
  }, [])

  useEffect(() => {

    const loggedUserJSON = window.localStorage.getItem('loggedNoteappUser')

    if (loggedUserJSON) {

      const user = JSON.parse(loggedUserJSON)

      setUser(user)

      noteService.setToken(user.token)
    }
  }, [])  

  const addNote = (event) => {

    event.preventDefault()

    const noteObject = {
      content: newNote,
      date: new Date().toISOString(),
      important: Math.random() > 0.5,
    }

    noteService
      .create(noteObject)
        .then(returnedNote => {
        setNotes(notes.concat(returnedNote))
        setNewNote('')
      })
  }

  const toggleImportanceOf = id => {

    const note = notes.find(n => n.id === id)

    const changedNote = { ...note, important: !note.important }
  
    noteService
    .update(id, changedNote)
      .then(returnedNote => {
      setNotes(notes.map(note => note.id !== id ? note : returnedNote))
    })
    .catch(error => {
      setErrorMessage(
        `Note '${note.content}' was already removed from server`
      )
      setTimeout(() => {

        setErrorMessage(null)
      }, 10000)
    })    
  }

  const handleNoteChange = (event) => {

    console.log(event.target.value)

    setNewNote(event.target.value)
  }

  const notesToShow = showAll
  ? notes
  : notes.filter(note => note.important)

  const handleLogin = async (event) => {

    event.preventDefault()

    try {
      const user = await loginService.login({
        username, password,
      })

      noteService.setToken(user.token)

      console.log(username, user.token)

      window.localStorage.setItem(
        'loggedNoteappUser', JSON.stringify(user)
      ) 

      setUser(user)

      setUsername('')

      setPassword('')

    } catch (exception) {

      setErrorMessage('Error: credentials')

      setTimeout(() => {

        setErrorMessage(null)
      }, 10000)
    }
  }

  const loginForm = () => (
    <Togglable buttonLabel="log in">
      <LoginForm
        username={username}
        password={password}
        handleUsernameChange={({ target }) => setUsername(target.value)}
        handlePasswordChange={({ target }) => setPassword(target.value)}
        handleSubmit={handleLogin}
      />
    </Togglable>
  )

  const noteForm = () => (
    <Togglable buttonLabel="new note">
      <NoteForm
        onSubmit={addNote}
        value={newNote}
        handleChange={handleNoteChange}
      />
    </Togglable>
  )

  return (
    <div>
      <h1>Notes</h1>
      <Notification message={errorMessage} />

      {user === null ?
        loginForm() :
        <div>
          <p>{username} logged in</p>
          {noteForm()}
        </div>
      }

      <div>
        <button onClick={() => setShowAll(!showAll)}>
          show {showAll ? 'important' : 'all' }
        </button>
      </div>   
      <ul>
        {notesToShow.map(note => 
            <Note
              key={note.id}
              note={note} 
              toggleImportance={() => toggleImportanceOf(note.id)}
            />
        )}
      </ul>

      <Footer />
    </div>
  )
}

export default App