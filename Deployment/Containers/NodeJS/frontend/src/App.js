import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

// Configure axios
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = 10000;

// Request interceptor for auth token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling auth errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

const App = () => {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [isAuthMode, setIsAuthMode] = useState(true); // true for login, false for register

  // Authentication form state
  const [authForm, setAuthForm] = useState({
    name: '',
    email: '',
    password: ''
  });

  // Task form state
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: ''
  });

  // Check for existing auth token on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      fetchUserProfile();
    }
  }, []);

  // Fetch user profile
  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setUser(response.data.user);
      fetchTasks();
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      localStorage.removeItem('authToken');
    }
  };

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filter === 'completed') params.completed = true;
      if (filter === 'pending') params.completed = false;
      
      const response = await axios.get('/api/tasks', { params });
      setTasks(response.data.tasks);
    } catch (error) {
      setError('Failed to fetch tasks');
      console.error('Fetch tasks error:', error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user, fetchTasks]);

  // Authentication handlers
  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isAuthMode ? '/api/auth/login' : '/api/auth/register';
      const payload = isAuthMode 
        ? { email: authForm.email, password: authForm.password }
        : authForm;

      const response = await axios.post(endpoint, payload);
      
      localStorage.setItem('authToken', response.data.token);
      setUser(response.data.user);
      setAuthForm({ name: '', email: '', password: '' });
      
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Authentication failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setTasks([]);
    setAuthForm({ name: '', email: '', password: '' });
  };

  // Task handlers
  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!taskForm.title.trim()) return;

    try {
      setLoading(true);
      const response = await axios.post('/api/tasks', taskForm);
      setTasks([response.data.task, ...tasks]);
      setTaskForm({ title: '', description: '', priority: 'medium', dueDate: '' });
    } catch (error) {
      setError('Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (taskId, completed) => {
    try {
      const response = await axios.put(`/api/tasks/${taskId}`, { completed: !completed });
      setTasks(tasks.map(task => 
        task._id === taskId ? response.data.task : task
      ));
    } catch (error) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;

    try {
      await axios.delete(`/api/tasks/${taskId}`);
      setTasks(tasks.filter(task => task._id !== taskId));
    } catch (error) {
      setError('Failed to delete task');
    }
  };

  // Filter tasks based on current filter
  const filteredTasks = tasks.filter(task => {
    if (filter === 'completed') return task.completed;
    if (filter === 'pending') return !task.completed;
    return true;
  });

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff4757';
      case 'medium': return '#ffa502';
      case 'low': return '#2ed573';
      default: return '#747d8c';
    }
  };

  // Authentication form
  if (!user) {
    return (
      <div className="app">
        <div className="auth-container">
          <div className="auth-header">
            <h1>Task Manager</h1>
            <p>Node.js & React Full Stack Application</p>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleAuth} className="auth-form">
            <h2>{isAuthMode ? 'Login' : 'Register'}</h2>
            
            {!isAuthMode && (
              <input
                type="text"
                placeholder="Full Name"
                value={authForm.name}
                onChange={(e) => setAuthForm({...authForm, name: e.target.value})}
                required={!isAuthMode}
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
              placeholder="Password (min 6 characters)"
              value={authForm.password}
              onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
              required
              minLength="6"
            />
            
            <button type="submit" disabled={loading} className="auth-button">
              {loading ? 'Processing...' : (isAuthMode ? 'Login' : 'Register')}
            </button>
          </form>
          
          <p className="auth-toggle">
            {isAuthMode ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button"
              onClick={() => {
                setIsAuthMode(!isAuthMode);
                setError('');
              }}
              className="link-button"
            >
              {isAuthMode ? 'Register' : 'Login'}
            </button>
          </p>
          
          <div className="app-info">
            <p>🚀 Deployed on Docker</p>
            <p>👤 User:</p>
            <p>📅 {new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    );
  }

  // Main application
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Task Manager</h1>
          <div className="user-info">
            <span>Welcome, {user.name}!</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <main className="main-content">
        {/* Task creation form */}
        <section className="task-form-section">
          <h2>Create New Task</h2>
          <form onSubmit={handleCreateTask} className="task-form">
            <input
              type="text"
              placeholder="Task title"
              value={taskForm.title}
              onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
              required
            />
            
            <textarea
              placeholder="Task description (optional)"
              value={taskForm.description}
              onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
              rows="3"
            />
            
            <div className="form-row">
              <select
                value={taskForm.priority}
                onChange={(e) => setTaskForm({...taskForm, priority: e.target.value})}
              >
                <option value="low">Low Priority</option>
                <option value="medium">Medium Priority</option>
                <option value="high">High Priority</option>
              </select>
              
              <input
                type="date"
                value={taskForm.dueDate}
                onChange={(e) => setTaskForm({...taskForm, dueDate: e.target.value})}
              />
            </div>
            
            <button type="submit" disabled={loading} className="create-button">
              {loading ? 'Creating...' : 'Create Task'}
            </button>
          </form>
        </section>

        {/* Task filters */}
        <section className="filters-section">
          <h2>Tasks ({filteredTasks.length})</h2>
          <div className="filters">
            <button
              onClick={() => setFilter('all')}
              className={filter === 'all' ? 'filter-button active' : 'filter-button'}
            >
              All ({tasks.length})
            </button>
            <button
              onClick={() => setFilter('pending')}
              className={filter === 'pending' ? 'filter-button active' : 'filter-button'}
            >
              Pending ({tasks.filter(t => !t.completed).length})
            </button>
            <button
              onClick={() => setFilter('completed')}
              className={filter === 'completed' ? 'filter-button active' : 'filter-button'}
            >
              Completed ({tasks.filter(t => t.completed).length})
            </button>
          </div>
        </section>

        {/* Task list */}
        <section className="tasks-section">
          {loading && <div className="loading">Loading tasks...</div>}
          
          {!loading && filteredTasks.length === 0 && (
            <div className="empty-state">
              <p>No tasks found. Create your first task above!</p>
            </div>
          )}
          
          <div className="tasks-grid">
            {filteredTasks.map(task => (
              <div key={task._id} className={`task-card ${task.completed ? 'completed' : ''}`}>
                <div className="task-header">
                  <h3>{task.title}</h3>
                  <div 
                    className="priority-indicator"
                    style={{ backgroundColor: getPriorityColor(task.priority) }}
                    title={`${task.priority} priority`}
                  />
                </div>
                
                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}
                
                <div className="task-meta">
                  <span className="task-date">
                    Created: {formatDate(task.createdAt)}
                  </span>
                  {task.dueDate && (
                    <span className="task-due">
                      Due: {formatDate(task.dueDate)}
                    </span>
                  )}
                </div>
                
                <div className="task-actions">
                  <button
                    onClick={() => handleToggleTask(task._id, task.completed)}
                    className={task.completed ? 'uncomplete-button' : 'complete-button'}
                  >
                    {task.completed ? 'Mark Pending' : 'Mark Complete'}
                  </button>
                  
                  <button
                    onClick={() => handleDeleteTask(task._id)}
                    className="delete-button"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;