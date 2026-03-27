import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../services/api';
import { User, Mail, Lock, ShieldCheck, Film, Sparkles, Video } from 'lucide-react';
import './Auth.css';

const mosaicImages = [
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBFOxoytf8-Mqzi0Qhm8jtYnLPFttheWLuGWxJZsd6D6O6JOKGlwV64jKLyhf_gjpgCM-dXF3SphuK2-1kIrkW8IMipoqCo-vGiJyTcsmMt4RMSDOCX-4rwT1Ym0UNn4tlBPn8Gn9zHMuqDgKpdPm8uJdNRpLwW5LRHieq8P-AJNbqS3_Cm_yr4O_yAflJpOjmumpaMBdBRmKc_msg6D0mWNO0QmT5ocbxdRIOM15NK72rth2Mshfje3hmWCEFHdJHtsK8h9NX7gg",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuCxVrHb3tfHBzEAlkdfOL1cN5Pv2w1FaA9zU51tPm6EqnMlN_N9RfYjVE_Ca4P9_nUYSs2driwRQa3_k60KFNqZW9iLOvMD9MTSRulXS8grusTyur5yueR2ybsSvGmjsJdKlOSaHhlbHdVgF2ddoxFHBH6LEZmBS6dWYk7twSr2IdAw_FBE-9kReLnTzo_sBPfbYYwv58wvtLZKR859stGormDMCbxRcmvDiQqJV43ghxFFY_wUgZZYzDO9h2nCmD-QKwmh1q-DsQ",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBB_-HcyCFzUpBohWdabyWn_WxSJAx5f4R_IieeoDEqNu_ymMizMPXgmihq43SkvflxHssGvA5F1qrlMLdbn4XVw_Bti2NW1xhHP48rB5vvT_HgONiEMZyai-MaNM1MwE0MJFBgQyH5dPYnTNKAbLnhLAlW8qsqu_FClyIObV9GYTkg7TUkgAI2HTgRnwNnMDTbYRHR6xNktx7AznYMgeJqpj7aC7JHuJHeS5H-MKZ8U8vAg0C_LBMWnxCA1ZnD4m5C91sqxIJ3Iw",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBVDtapXoaFwuP0lqXoGtgVdFAAXp_RycI6LFg0A2zDgzwJWofJr8fKUhTKnRL7YeuvA8P9GecJoF1zdpUCVxrYjukOu4Pyt7DNqQzmURL6kfY8crKGXU46SagR0bG6ZKuSrjSITvC0lpEQHHFJKfqMauZMb_RnMmX7Ry4Fzs8Mb5TYdkDGXAfkXfdQoJOdLxGaTyfg1RmcmdIMFXAIRyj1aYGlRkqoZ-HJWkE3ZotdPrjGesowiL8-UURr4dRAXzT0ts3SEMwFTQ",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAQZa6ngt1S52DObT1cLjc6J8p32M2Zlf2s9MjllJPDmlgpMohIZUecSoI5H2nNCgX1F6T_dL-7ZJHqCrpekL_imskWwnKXo8euH9x6t_RFs7HEOojl7kQ3kilHf6Ioa57NdznYYP-HSf3w2bbVMsum6QgLYd9QXwSvewiYmhHa8a8E6YNci0gYmO2jaTT2wmkcixFaC13DByr_y-oalPvZ87vrCe3EQkMlvNT3uVSN7RJWmUALj9-Z7QgX5P-p2duwfn_29L0X1g",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAYqmPXQ1HURV9sq8K-64zzyx0MwYBNGayZzY1wwDU6N0iMm6CsJ-2AYcDxsNX9LXqwhUeTwWfHs5SM6UhCpNXPbxXD2U8aADPaJ13eGZ5lm1b7CNtqT2_De0pcwfK2etQGEkfU0Nf8TjxVHQsBZtuRBD-Y9vffDb8FghhYLhVysET2lENm0Go0mPBkhwtl-Qo6U_EDO2wQIXA25GCozrWndm1WFvHAQBdtdg-zzSdryW0JcN5MQNR7re1K9Pb9mar6g3tdu11g3w",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuCoiWH_4-Sunx2x7NqDilPQLjzz6BS0xNYhV9K8HwnQjvWMNymG-U2moLxyGFQroxG64zBfhyRqJy5DfYTXsZvDV7aMpgmX9LcqKTESywmz-JILm6YVrek4kR3vMp-mgxXUblIq3kP6JwRcLH0Hwq1TCBt9mclZGW3YFeEuiVhO6gzkgGXSIhUJ5LGLg95XwJTa7IgyPDDU69z3jWs3vXR3ATr3WR_GAKLdQVNYTX-6LoWE2GSpJp7YSynifWEUPV4i_vmOQf1rWw",
  "https://lh3.googleusercontent.com/aida-public/AB6AXuAKVCI8VLp31gdFpBcf_26ATWTk6DWv9v8MATEkuPZTIpP-lUTHc9eCLjLnNfbSE84YWGJV8q7Z1Dwfnwzfauecnby7TvGq1HPJMUnXvi6rAEAd2336UzYLslyPaUV2mtH2ELnk7myArJ3mNefaXFOJgJvHI2DgRPK1gaWHIm-itZk1u3jANLMYxiTfa8OiX0f69hSap2rr8aPtNAZPaI3YXhLonOOlaS6Zey2pJ6YDIllptQiy8QQ3DR_uK1seoDhoQHw75iQsPA"
];

export default function Signup({ onAuth }) {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await signup(formData);
      onAuth(res.data.user, res.data.token);
      navigate('/onboarding');
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during signup.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Background Collage Layer */}
      <div className="auth-bg-collage">
        {mosaicImages.map((src, idx) => (
          <img key={`bg-${idx}`} src={src} alt="Decorative" />
        ))}
      </div>
      
      <div className="auth-tonal-overlay"></div>

      <main className="auth-main">
        <div className="auth-container">
          
          <div className="auth-header-brand">
            <Link to="/" className="auth-brand-title">mov<span>AI</span></Link>
            <p className="auth-brand-subtitle">The Digital Projection</p>
          </div>

          <div className="auth-card">
            <header className="auth-card-header">
              <h2 className="auth-card-title">Join movAI</h2>
              <p className="auth-card-subtitle">Create your cinematic identity to start curating.</p>
            </header>

            {error && <div className="auth-error">{error}</div>}

            <form className="auth-form" onSubmit={handleSubmit}>
              
              <div className="form-group-floating">
                <div className="form-icon-left">
                  <User size={20} />
                </div>
                <input 
                  type="text" 
                  id="name" 
                  name="name" 
                  placeholder=" " 
                  value={formData.name} 
                  onChange={handleChange} 
                  required 
                />
                <label htmlFor="name">Display Name</label>
                <div className="form-group-indicator"></div>
              </div>

              <div className="form-group-floating">
                <div className="form-icon-left">
                  <ShieldCheck size={20} />
                </div>
                <input 
                  type="text" 
                  id="username" 
                  name="username" 
                  placeholder=" " 
                  value={formData.username} 
                  onChange={handleChange} 
                />
                <label htmlFor="username">Username (Optional)</label>
                <div className="form-group-indicator"></div>
              </div>

              <div className="form-group-floating">
                <div className="form-icon-left">
                  <Mail size={20} />
                </div>
                <input 
                  type="email" 
                  id="email" 
                  name="email" 
                  placeholder=" " 
                  value={formData.email} 
                  onChange={handleChange} 
                  required 
                />
                <label htmlFor="email">Email address</label>
                <div className="form-group-indicator"></div>
              </div>

              <div className="form-group-floating">
                <div className="form-icon-left">
                  <Lock size={20} />
                </div>
                <input 
                  type="password" 
                  id="password" 
                  name="password" 
                  placeholder=" " 
                  value={formData.password} 
                  onChange={handleChange} 
                  required 
                />
                <label htmlFor="password">Password</label>
                <div className="form-group-indicator"></div>
              </div>

              <button type="submit" className="auth-submit-btn" disabled={loading}>
                {loading ? 'Creating Account...' : 'Create Account'}
              </button>
            </form>

            <div className="auth-nav-link">
              Already have an account? 
              <Link to="/login">Sign in</Link>
            </div>

            <div className="auth-flare">
              <div className="auth-flare-line left"></div>
              <div className="auth-flare-icons">
                <Film size={20} />
                <Sparkles size={20} />
                <Video size={20} />
              </div>
              <div className="auth-flare-line right"></div>
            </div>

          </div>
        </div>
      </main>

      <footer className="auth-footer">
        <div className="auth-footer-brand">movAI</div>
        <p className="auth-footer-copy">© 2024 movAI Cinematic. All rights reserved.</p>
        <div className="auth-footer-links">
          <Link to="#">Privacy Policy</Link>
          <Link to="#">Terms of Service</Link>
          <Link to="#">Help Center</Link>
        </div>
      </footer>
    </div>
  );
}
