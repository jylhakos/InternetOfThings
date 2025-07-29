const { GraphQLObjectType, GraphQLString, GraphQLSchema, GraphQLList, GraphQLBoolean, GraphQLNonNull } = require('graphql');
const { v4: uuidv4 } = require('uuid');

// In-memory store for notes (replace with database in production)
let notes = [
  {
    id: '1',
    content: 'Welcome to GraphQL Notes.',
    date: new Date().toISOString(),
    important: true
  },
  {
    id: '2',
    content: 'This is a sample note for IoT messaging',
    date: new Date().toISOString(),
    important: false
  }
];

// Note Type Definition
const NoteType = new GraphQLObjectType({
  name: 'Note',
  fields: () => ({
    id: { type: GraphQLString },
    content: { type: GraphQLString },
    date: { type: GraphQLString },
    important: { type: GraphQLBoolean }
  })
});

// Root Query
const RootQuery = new GraphQLObjectType({
  name: 'RootQueryType',
  fields: {
    // Get all notes
    notes: {
      type: new GraphQLList(NoteType),
      resolve() {
        return notes;
      }
    },
    // Get single note by ID
    note: {
      type: NoteType,
      args: {
        id: { type: GraphQLString }
      },
      resolve(parent, args) {
        return notes.find(note => note.id === args.id);
      }
    }
  }
});

// Mutations
const Mutation = new GraphQLObjectType({
  name: 'Mutation',
  fields: {
    // Add a new note
    addNote: {
      type: NoteType,
      args: {
        content: { type: new GraphQLNonNull(GraphQLString) },
        important: { type: GraphQLBoolean }
      },
      resolve(parent, args) {
        const newNote = {
          id: uuidv4(),
          content: args.content,
          date: new Date().toISOString(),
          important: args.important !== undefined ? args.important : Math.random() > 0.5
        };
        notes.push(newNote);
        return newNote;
      }
    },
    // Update note importance
    toggleImportance: {
      type: NoteType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLString) }
      },
      resolve(parent, args) {
        const note = notes.find(note => note.id === args.id);
        if (note) {
          note.important = !note.important;
          return note;
        }
        return null;
      }
    },
    // Delete a note
    deleteNote: {
      type: NoteType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLString) }
      },
      resolve(parent, args) {
        const noteIndex = notes.findIndex(note => note.id === args.id);
        if (noteIndex !== -1) {
          const deletedNote = notes[noteIndex];
          notes.splice(noteIndex, 1);
          return deletedNote;
        }
        return null;
      }
    }
  }
});

module.exports = new GraphQLSchema({
  query: RootQuery,
  mutation: Mutation
});
