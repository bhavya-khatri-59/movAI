import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getUserProfile, getMe, getFollowers, getFollowing, followUser } from '../services/api';
import './Profile.css';

export default function Profile({ currentUser }) {
  const { id } = useParams();
  const userId = id ? parseInt(id) : currentUser.id;
  const isOwnProfile = userId === currentUser.id;

  const [profile, setProfile] = useState(null);
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState('stats');

  useEffect(() => {
    const loadProfile = async () => {
      try {
        if (isOwnProfile) {
          const res = await getMe();
          setProfile(res.data.user);
        } else {
          const res = await getUserProfile(userId);
          setProfile(res.data.user);
        }
        const followersRes = await getFollowers(userId);
        setFollowers(followersRes.data.followers || []);
        const followingRes = await getFollowing(userId);
        setFollowing(followingRes.data.following || []);
        if (!isOwnProfile) {
          const myFollowing = await getFollowing(currentUser.id);
          setIsFollowing(myFollowing.data.following?.some(u => u.id === userId) || false);
        }
      } catch (e) { console.error(e); }
    };
    loadProfile();
  }, [userId, isOwnProfile, currentUser.id]);

  const handleFollow = async () => {
    const res = await followUser(userId);
    setIsFollowing(res.data.following);
  };

  if (!profile) return <div className="page-content container"><div className="skeleton" style={{ height: 300 }} /></div>;

  return (
    <div className="page-content">
      <div className="container">
        {/* Profile Header */}
        <div className="profile-header glass-card animate-fade-in-up">
          <div className="profile-banner" />
          <div className="profile-info-row">
            <div className="profile-avatar-large">
              {profile.name?.charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <h1>{profile.name}</h1>
              <p className="profile-username">@{profile.username}</p>
              <p className="profile-bio">{profile.bio || 'Movie enthusiast'}</p>
              <p className="profile-joined">Joined {new Date(profile.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p>
            </div>
            <div className="profile-action">
              {!isOwnProfile && (
                <button className={`btn ${isFollowing ? 'btn-primary' : 'btn-outline'}`} onClick={handleFollow}>
                  {isFollowing ? 'Following' : 'Follow'}
                </button>
              )}
            </div>
          </div>
          <div className="profile-stats">
            <div className="profile-stat">
              <span className="stat-value">{profile.movies_watched || 0}</span>
              <span className="stat-name">Movies</span>
            </div>
            <div className="profile-stat">
              <span className="stat-value">{profile.reviews_count || 0}</span>
              <span className="stat-name">Reviews</span>
            </div>
            <div className="profile-stat">
              <span className="stat-value">{profile.following_count || 0}</span>
              <span className="stat-name">Following</span>
            </div>
            <div className="profile-stat">
              <span className="stat-value">{profile.followers_count || 0}</span>
              <span className="stat-name">Followers</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="profile-tabs">
          {['stats', 'followers', 'following'].map(tab => (
            <button key={tab} className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab)}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="profile-tab-content">
          {activeTab === 'stats' && (
            <div className="stats-content glass-card" style={{ padding: 'var(--space-xl)' }}>
              <h3 style={{ marginBottom: 'var(--space-md)' }}>Activity Overview</h3>
              <p style={{ color: 'var(--text-secondary)' }}>
                {profile.name} has watched {profile.movies_watched || 0} movies and written {profile.reviews_count || 0} reviews.
              </p>
            </div>
          )}
          {activeTab === 'followers' && (
            <div className="user-list">
              {followers.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>No followers yet</p> : null}
              {followers.map(u => (
                <Link key={u.id} to={`/profile/${u.id}`} className="user-item glass-card" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="user-avatar-small">{u.name?.charAt(0)}</div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{u.name}</div>
                    <div style={{ fontSize: 'var(--font-label)', color: 'var(--text-muted)' }}>@{u.username}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
          {activeTab === 'following' && (
            <div className="user-list">
              {following.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>Not following anyone yet</p> : null}
              {following.map(u => (
                <Link key={u.id} to={`/profile/${u.id}`} className="user-item glass-card" style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="user-avatar-small">{u.name?.charAt(0)}</div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{u.name}</div>
                    <div style={{ fontSize: 'var(--font-label)', color: 'var(--text-muted)' }}>@{u.username}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
