import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;

const TodoApp = () => {
    const [todos, setTodos] = useState([]);
    const [newTodo, setNewTodo] = useState({ title: '', description: '' });
    const [user, setUser] = useState(null);
    const [authForm, setAuthForm] = useState({ email: '', password: '', name: '' });
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Set auth token in axios headers
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            fetchUser();
        }
    }, []);

    const fetchUser = async () => {
        try {
            const response = await axios.get('/api/users/me');
            setUser(response.data);
            fetchTodos();
        } catch (error) {
            console.error('Error fetching user:', error);
            localStorage.removeItem('access_token');
            delete axios.defaults.headers.common['Authorization'];
        }
    };

    const fetchTodos = async () => {
        try {
            const response = await axios.get('/api/todos');
            setTodos(response.data);
        } catch (error) {
            setError('Error fetching todos');
        }
    };

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
            const payload = isLogin 
                ? { email: authForm.email, password: authForm.password }
                : authForm;

            const response = await axios.post(endpoint, payload);

            if (isLogin) {
                localStorage.setItem('access_token', response.data.access_token);
                axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
                fetchUser();
            } else {
                setIsLogin(true);
                setError('Registration successful! Please login.');
            }
        } catch (error) {
            setError(error.response?.data?.detail || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        delete axios.defaults.headers.common['Authorization'];
        setUser(null);
        setTodos([]);
    };

    const addTodo = async (e) => {
        e.preventDefault();
        if (!newTodo.title.trim()) return;

        try {
            const response = await axios.post('/api/todos', newTodo);
            setTodos([response.data, ...todos]);
            setNewTodo({ title: '', description: '' });
        } catch (error) {
            setError('Error adding todo');
        }
    };

    const toggleTodo = async (id, completed) => {
        try {
            const response = await axios.put(`/api/todos/${id}`, { completed: !completed });
            setTodos(todos.map(todo => 
                todo.id === id ? response.data : todo
            ));
        } catch (error) {
            setError('Error updating todo');
        }
    };

    const deleteTodo = async (id) => {
        try {
            await axios.delete(`/api/todos/${id}`);
            setTodos(todos.filter(todo => todo.id !== id));
        } catch (error) {
            setError('Error deleting todo');
        }
    };

    if (!user) {
        return (
            <div className="auth-container">
                <h2>{isLogin ? 'Login' : 'Register'}</h2>
                {error && <div className="error">{error}</div>}
                
                <form onSubmit={handleAuth}>
                    {!isLogin && (
                        <input
                            type="text"
                            placeholder="Name"
                            value={authForm.name}
                            onChange={(e) => setAuthForm({...authForm, name: e.target.value})}
                            required
                        />
                    )}
                    <input
                        type="email"
                        placeholder="Email"
                        value={authForm.email}
                        onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={authForm.password}
                        onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                        required
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Loading...' : (isLogin ? 'Login' : 'Register')}
                    </button>
                </form>
                
                <p>
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button 
                        type="button" 
                        onClick={() => setIsLogin(!isLogin)}
                        className="link-button"
                    >
                        {isLogin ? 'Register' : 'Login'}
                    </button>
                </p>
            </div>
        );
    }

    return (
        <div className="todo-app">
            <header>
                <h1>Todo App</h1>
                <div className="user-info">
                    <span>Welcome, {user.name}!</span>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </header>

            {error && <div className="error">{error}</div>}

            <form onSubmit={addTodo} className="todo-form">
                <input
                    type="text"
                    placeholder="Todo title"
                    value={newTodo.title}
                    onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                    required
                />
                <input
                    type="text"
                    placeholder="Description (optional)"
                    value={newTodo.description}
                    onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                />
                <button type="submit">Add Todo</button>
            </form>

            <div className="todo-list">
                {todos.map(todo => (
                    <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                        <div className="todo-content">
                            <h3>{todo.title}</h3>
                            {todo.description && <p>{todo.description}</p>}
                            <small>Created: {new Date(todo.created_at).toLocaleDateString()}</small>
                        </div>
                        <div className="todo-actions">
                            <button 
                                onClick={() => toggleTodo(todo.id, todo.completed)}
                                className={todo.completed ? 'uncomplete' : 'complete'}
                            >
                                {todo.completed ? 'Undo' : 'Complete'}
                            </button>
                            <button 
                                onClick={() => deleteTodo(todo.id)}
                                className="delete"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TodoApp;