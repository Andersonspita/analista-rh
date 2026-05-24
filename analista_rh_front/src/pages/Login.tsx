import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Card } from '../components/Card';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Lock, User } from 'lucide-react';
import { ThemeToggle } from '../components/ThemeToggle';
import { GoogleLogin } from '@react-oauth/google';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.post('/auth/login', { username, password });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao realizar login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      
      <div style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
        <ThemeToggle />
      </div>

      <div className="container" style={{ maxWidth: '400px' }}>
        <Card className="animate-fade-in">
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <img src="/logo.png" alt="Horizon ATS Logo" style={{ width: '80px', height: '80px', margin: '0 auto 1rem', borderRadius: '1rem', objectFit: 'cover' }} />
            <h1 className="gradient-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Horizon ATS</h1>
            <p>Faça login para continuar</p>
          </div>

          <form onSubmit={handleLogin}>
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', top: '2.4rem', left: '1rem', color: 'var(--text-secondary)' }}>
                <User size={18} />
              </div>
              <Input
                label="Usuário"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ex: admin"
                style={{ paddingLeft: '2.5rem' }}
                required
              />
            </div>

            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', top: '2.4rem', left: '1rem', color: 'var(--text-secondary)' }}>
                <Lock size={18} />
              </div>
              <Input
                label="Senha"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{ paddingLeft: '2.5rem' }}
                required
              />
            </div>

            {error && (
              <div style={{ 
                color: '#ef4444', 
                backgroundColor: 'rgba(239, 68, 68, 0.1)', 
                padding: '0.75rem', 
                borderRadius: '0.5rem',
                marginBottom: '1rem',
                fontSize: '0.875rem',
                textAlign: 'center'
              }}>
                {error}
              </div>
            )}

            <Button type="submit" fullWidth disabled={isLoading}>
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>
            
            <div style={{ margin: '1.5rem 0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
              <span style={{ padding: '0 1rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>OU</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <GoogleLogin
                onSuccess={async (credentialResponse) => {
                  try {
                    setIsLoading(true);
                    const res = await api.post('/auth/google-login', { credential: credentialResponse.credential });
                    if (res.data.access_token) {
                      localStorage.setItem('token', res.data.access_token);
                      navigate('/');
                    }
                  } catch (err: any) {
                    setError(err.response?.data?.detail || 'Erro ao realizar login pelo Google');
                  } finally {
                    setIsLoading(false);
                  }
                }}
                onError={() => {
                  setError('Falha ao tentar login com o Google');
                }}
                theme="filled_black"
                text="continue_with"
                shape="rectangular"
              />
            </div>

          </form>
        </Card>
      </div>
    </div>
  );
};
