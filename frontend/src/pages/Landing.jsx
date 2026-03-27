import { Link } from 'react-router-dom';
import { Film, Sparkles, Video, BrainCircuit, Users, Smile, ArrowRight, Share2, Globe } from 'lucide-react';
import './Landing.css';

export default function Landing() {
  const mosaicImages = [
    "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg", // Inception
    "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", // Interstellar
    "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg", // Dune
    "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", // The Dark Knight
    "https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg", // Avatar
    "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg", // Blade Runner 2049
    "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg", // Spider-Man
    "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg", // Avengers
    "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg"  // Mad Max
  ];

  return (
    <div className="landing-page">
      {/* Top Navbar Simulation */}
      <nav style={{ position: 'fixed', top: 0, width: '100%', zIndex: 100, background: 'rgba(11, 12, 31, 0.4)', backdropFilter: 'blur(30px)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', maxWidth: 1400, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.05em', textDecoration: 'none' }}>
              mov<span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
            </Link>
          </div>
          <div style={{ display: 'flex', gap: '2rem' }} className="hidden md-flex">
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <Link to="/login" style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>Sign In</Link>
            <Link to="/signup" className="btn btn-hero-primary" style={{ padding: '0.5rem 1.5rem', fontSize: '1rem', borderRadius: '0.75rem' }}>
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero-section">
        <div className="hero-glow"></div>
        <div className="hero-bg-blur-1"></div>
        <div className="hero-bg-blur-2"></div>
        
        {/* Floating Poster Mosaic */}
        <div className="hero-mosaic">
          {[0, 1, 2, 3, 4, 5].map((colIndex) => (
            <div key={colIndex} className="mosaic-col">
              <div className="mosaic-img"><img src={mosaicImages[colIndex]} alt="Movie decorative" /></div>
              {colIndex < 3 && <div className="mosaic-img"><img src={mosaicImages[colIndex + 6]} alt="Movie decorative" /></div>}
            </div>
          ))}
        </div>

        <div className="hero-content animate-fade-in-up">
          <div>
            <span className="hero-badge">Introducing The Future of Cinema</span>
            <h1 className="hero-title">
              Discover Movies <br />
              <span className="highlight">You'll Love</span>
            </h1>
            <p className="hero-subtitle">
              AI-powered recommendations, social discovery, and mood-based browsing — all in one beautiful platform.
            </p>
            <div className="hero-actions">
              <Link to="/signup" className="btn-hero btn-hero-primary">Get Started Free</Link>
            </div>
            
            {/* Visual Flare Icons */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginTop: '3rem', opacity: 0.4 }}>
              <div style={{ height: '1px', width: '3rem', background: 'linear-gradient(to right, transparent, var(--outline))' }}></div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <Film size={20} color="var(--outline)" />
                <Sparkles size={20} color="var(--outline)" />
                <Video size={20} color="var(--outline)" />
              </div>
              <div style={{ height: '1px', width: '3rem', background: 'linear-gradient(to left, transparent, var(--outline))' }}></div>
            </div>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Reimagined Exploration</h2>
            <div className="section-divider"></div>
          </div>

          <div className="features-grid">
            <div className="feature-card glass-card">
              <div className="feature-icon-wrapper" style={{ background: 'rgba(172, 163, 255, 0.1)' }}>
                <BrainCircuit size={32} color="var(--accent-primary)" strokeWidth={1.5} />
              </div>
              <h3 className="feature-title">AI Recommendations</h3>
              <p className="feature-desc">
                Our neural network learns your taste profile to suggest hidden gems you've never heard of but will absolutely adore.
              </p>
              <div className="feature-link group">
                <span>Learn more</span>
                <ArrowRight size={16} />
              </div>
            </div>

            <div className="feature-card glass-card">
              <div className="feature-icon-wrapper" style={{ background: 'rgba(177, 144, 254, 0.1)' }}>
                <Users size={32} color="var(--accent-secondary)" strokeWidth={1.5} />
              </div>
              <h3 className="feature-title">Social Discovery</h3>
              <p className="feature-desc">
                See what your friends are watching and discover trending titles within communities of like-minded cinephiles.
              </p>
              <div className="feature-link group">
                <span>Join circles</span>
                <ArrowRight size={16} />
              </div>
            </div>

            <div className="feature-card glass-card">
              <div className="feature-icon-wrapper" style={{ background: 'rgba(255, 158, 202, 0.1)' }}>
                <Smile size={32} color="var(--accent-tertiary)" strokeWidth={1.5} />
              </div>
              <h3 className="feature-title">Mood-Based Browsing</h3>
              <p className="feature-desc">
                Tired of scrolling? Pick a mood—from 'Melancholic' to 'Adrenaline Rush'—and let us curate the perfect evening.
              </p>
              <div className="feature-link group">
                <span>Set your mood</span>
                <ArrowRight size={16} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="process-section">
        <div className="container">
          <div className="process-header">
            <div>
              <span className="process-pretitle">Process</span>
              <h2 className="process-title">Start Your Journey <br />In Three Steps</h2>
            </div>
            <p className="process-subtitle">We've streamlined the discovery process so you spend less time searching and more time watching.</p>
          </div>

          <div className="process-grid">
            <div className="process-step">
              <div className="process-step-num">01</div>
              <div className="process-step-content">
                <h4 className="process-step-title">Sign Up</h4>
                <p className="process-step-desc">Create your personal profile in seconds. Connect your streaming services to sync your history effortlessly.</p>
              </div>
            </div>
            
            <div className="process-step">
              <div className="process-step-num">02</div>
              <div className="process-step-content">
                <h4 className="process-step-title">Rate Movies</h4>
                <p className="process-step-desc">Rate just 5 movies you've seen recently. Our AI begins mapping your cinematic DNA immediately.</p>
              </div>
            </div>

            <div className="process-step">
              <div className="process-step-num">03</div>
              <div className="process-step-content">
                <h4 className="process-step-title">Get Personalized Picks</h4>
                <p className="process-step-desc">Enjoy a curated feed of recommendations tailored specifically to your unique tastes and current mood.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card">
            <div className="cta-gradient"></div>
            <div className="cta-content">
              <h2 className="cta-title">Ready to meet your next favorite movie?</h2>
              <p className="cta-subtitle">Join over 500,000 cinephiles discovering the future of film selection today.</p>
              <div className="cta-actions">
                <Link to="/signup" className="cta-btn-primary">Join Now</Link>
              </div>
            </div>
            <div className="cta-blur-1"></div>
            <div className="cta-blur-2"></div>
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="footer">
        <div className="footer-content" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', maxWidth: '1400px', margin: '0 auto' }}>
          <div className="footer-brand" style={{ textAlign: 'left', marginBottom: 0 }}>
            <div className="footer-logo">movAI</div>
            <p className="footer-copyright">© 2024 movAI. The Digital Projection. Designed for the ultimate cinematic experience.</p>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ width: '2.5rem', height: '2.5rem', borderRadius: '50%', background: 'var(--bg-elevated)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
               <Share2 size={18} />
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
