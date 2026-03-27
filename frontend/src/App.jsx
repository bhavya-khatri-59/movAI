import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Onboarding from './pages/Onboarding';
import Home from './pages/Home';
import MovieDetails from './pages/MovieDetails';
import Profile from './pages/Profile';
import Search from './pages/Search';
import SocialFeed from './pages/SocialFeed';
import './App.css';

function AppContent({ user, setUser, handleAuth, handleLogout, loading }) {
  const location = useLocation();
  const hideNavbar = ['/', '/login', '/signup', '/onboarding'].includes(location.pathname);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0b0c1f' }}>
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <>
      {user && !hideNavbar && <Navbar user={user} onLogout={handleLogout} />}
      <Routes>
        <Route path="/" element={!user ? <Landing /> : (user.onboarded ? <Navigate to="/home" /> : <Navigate to="/onboarding" />)} />
        <Route path="/login" element={!user ? <Login onAuth={handleAuth} /> : (user.onboarded ? <Navigate to="/home" /> : <Navigate to="/onboarding" />)} />
        <Route path="/signup" element={!user ? <Signup onAuth={handleAuth} /> : (user.onboarded ? <Navigate to="/home" /> : <Navigate to="/onboarding" />)} />
        <Route path="/onboarding" element={user && !user.onboarded ? <Onboarding user={user} setUser={setUser} /> : <Navigate to="/home" />} />
        <Route path="/home" element={user ? <Home user={user} /> : <Navigate to="/login" />} />
        <Route path="/movie/:id" element={user ? <MovieDetails /> : <Navigate to="/login" />} />
        <Route path="/profile/:id?" element={user ? <Profile currentUser={user} /> : <Navigate to="/login" />} />
        <Route path="/search" element={user ? <Search /> : <Navigate to="/login" />} />
        <Route path="/feed" element={user ? <SocialFeed /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('movai_token');
    if (token) {
      getMe()
        .then((res) => setUser(res.data.user))
        .catch(() => localStorage.removeItem('movai_token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleAuth = (userData, token) => {
    localStorage.setItem('movai_token', token);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('movai_token');
    setUser(null);
  };

  return (
    <Router>
      <AppContent user={user} setUser={setUser} handleAuth={handleAuth} handleLogout={handleLogout} loading={loading} />
    </Router>
  );
}

export default App;
