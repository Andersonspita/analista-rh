import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { ThemeToggle } from '../components/ThemeToggle';
import { ResumePDFDocument } from '../components/ResumePDFTemplate';
import { PDFDownloadLink } from '@react-pdf/renderer';
import { UploadCloud, FileText, CheckCircle, AlertTriangle, LogOut, Users, Shield, Clock } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [parsedResume, setParsedResume] = useState<any>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // User Profile State
  const [userProfile, setUserProfile] = useState<any>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [adminUsersList, setAdminUsersList] = useState<any[]>([]);

  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/users/me');
      setUserProfile(res.data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const fetchAdminUsersList = async () => {
    try {
      const res = await api.get('/users/admin/list');
      setAdminUsersList(res.data);
    } catch (err) {
      alert('Erro ao buscar lista de usuários');
    }
  };

  const handleStatusChange = async (username: string, newStatus: string) => {
    try {
      await api.put(`/users/admin/status/${username}`, { status: newStatus });
      fetchAdminUsersList(); // refresh list
    } catch (err) {
      alert('Erro ao atualizar status');
    }
  };

  const toggleAdminPanel = () => {
    if (!showAdminPanel) {
      fetchAdminUsersList();
    }
    setShowAdminPanel(!showAdminPanel);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Resto das funções...
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('/parse-resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setParsedResume(res.data);
      alert('Currículo extraído com sucesso!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro ao processar currículo');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!parsedResume || !jobDescription) return;
    setIsAnalyzing(true);
    try {
      const payload = {
        vaga: jobDescription,
        curriculo: parsedResume.dados_extraidos
      };
      const res = await api.post('/analyze-and-rebuild', payload);
      setAnalysisResult(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erro na análise');
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoadingProfile) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Carregando perfil...</div>;
  }

  // --- RENDERING TELA PENDENTE ---
  if (userProfile?.status === 'pending' || userProfile?.status === 'blocked') {
    return (
      <div style={{ minHeight: '100vh', padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <header style={{ position: 'absolute', top: '2rem', right: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <ThemeToggle />
          <Button variant="outline" onClick={handleLogout} style={{ padding: '0.5rem 1rem' }}>
            <LogOut size={18} /> Sair
          </Button>
        </header>
        <Card style={{ maxWidth: '500px', textAlign: 'center' }}>
          {userProfile?.status === 'pending' ? (
            <>
              <Clock size={64} style={{ margin: '0 auto 1rem', color: '#f59e0b' }} />
              <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Sua conta está em análise!</h1>
              <p style={{ color: 'var(--text-secondary)' }}>
                Nós recebemos o seu cadastro via Google. Para garantir a segurança da nossa IA, 
                um administrador precisa aprovar sua conta antes que você possa utilizar a plataforma.
              </p>
            </>
          ) : (
            <>
              <AlertTriangle size={64} style={{ margin: '0 auto 1rem', color: '#ef4444' }} />
              <h1 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Conta Bloqueada</h1>
              <p style={{ color: 'var(--text-secondary)' }}>
                O acesso à sua conta foi suspenso pelo administrador.
              </p>
            </>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', padding: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer' }} onClick={() => setShowAdminPanel(false)}>
          <img src="/logo.png" alt="Horizon ATS Logo" style={{ width: '40px', height: '40px', borderRadius: '0.5rem', objectFit: 'cover' }} />
          <h1 className="gradient-text" style={{ margin: 0 }}>Painel Horizon ATS</h1>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {userProfile?.role === 'admin' && (
            <Button variant={showAdminPanel ? "primary" : "outline"} onClick={toggleAdminPanel} style={{ padding: '0.5rem 1rem' }}>
              <Shield size={18} /> Admin
            </Button>
          )}
          <ThemeToggle />
          <Button variant="outline" onClick={handleLogout} style={{ padding: '0.5rem 1rem' }}>
            <LogOut size={18} /> Sair
          </Button>
        </div>
      </header>

      {showAdminPanel && userProfile?.role === 'admin' ? (
        <Card className="animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={24} className="gradient-text" /> Gerenciamento de Clientes
          </h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '1rem' }}>E-mail</th>
                  <th style={{ padding: '1rem' }}>Nível</th>
                  <th style={{ padding: '1rem' }}>Status Atual</th>
                  <th style={{ padding: '1rem' }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {adminUsersList.map(u => (
                  <tr key={u.username} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '1rem' }}>{u.email || u.username}</td>
                    <td style={{ padding: '1rem' }}>{u.role}</td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.875rem',
                        background: u.status === 'active' ? 'rgba(16, 185, 129, 0.1)' : u.status === 'pending' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        color: u.status === 'active' ? '#10b981' : u.status === 'pending' ? '#f59e0b' : '#ef4444'
                      }}>
                        {u.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', display: 'flex', gap: '0.5rem' }}>
                      {u.status !== 'active' && (
                        <button onClick={() => handleStatusChange(u.username, 'active')} style={{ padding: '0.25rem 0.5rem', background: '#10b981', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}>Aprovar</button>
                      )}
                      {u.status !== 'blocked' && (
                        <button onClick={() => handleStatusChange(u.username, 'blocked')} style={{ padding: '0.25rem 0.5rem', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}>Bloquear</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        
        {/* Upload Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <Card className="animate-fade-in">
            <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UploadCloud size={20} className="gradient-text" /> 1. Upload de Currículo
            </h2>
            <div style={{ 
              border: '2px dashed var(--border-color)', 
              borderRadius: '0.5rem', 
              padding: '2rem', 
              textAlign: 'center',
              marginTop: '1rem',
              transition: 'border-color 0.2s',
              cursor: 'pointer'
            }}
            onClick={() => document.getElementById('file-upload')?.click()}>
              <FileText size={40} style={{ margin: '0 auto', color: 'var(--text-secondary)' }} />
              <p style={{ marginTop: '1rem', fontWeight: '500' }}>
                {file ? file.name : 'Clique ou arraste um PDF aqui'}
              </p>
              <input 
                id="file-upload" 
                type="file" 
                accept="application/pdf" 
                onChange={handleFileChange} 
                style={{ display: 'none' }} 
              />
            </div>
            <Button 
              fullWidth 
              style={{ marginTop: '1rem' }} 
              disabled={!file || isUploading}
              onClick={handleUpload}
            >
              {isUploading ? 'Processando...' : 'Extrair Dados do PDF'}
            </Button>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>2. Descrição da Vaga</h2>
            <textarea
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '1rem',
                borderRadius: '0.5rem',
                border: '1px solid var(--border-color)',
                background: 'var(--surface-color)',
                color: 'var(--text-primary)',
                fontFamily: 'inherit',
                resize: 'vertical',
                outline: 'none'
              }}
              placeholder="Cole a descrição da vaga aqui..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
            <Button 
              fullWidth 
              style={{ marginTop: '1rem' }}
              disabled={!parsedResume || !jobDescription || isAnalyzing}
              onClick={handleAnalyze}
            >
              {isAnalyzing ? 'Analisando com IA...' : 'Analisar Aderência e Otimizar'}
            </Button>
          </Card>
        </div>

        {/* Results Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <Card className="animate-fade-in" style={{ animationDelay: '0.2s', minHeight: '100%' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>3. Resultados da Análise</h2>
            
            {!analysisResult && !isAnalyzing && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', color: 'var(--text-secondary)' }}>
                <CheckCircle size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                <p>Aguardando análise...</p>
              </div>
            )}

            {isAnalyzing && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px' }}>
                <div className="animate-spin" style={{ width: '40px', height: '40px', border: '4px solid var(--border-color)', borderTopColor: 'var(--primary)', borderRadius: '50%' }}></div>
                <p style={{ marginTop: '1rem' }} className="animate-pulse">A IA está processando...</p>
              </div>
            )}

            {analysisResult && !isAnalyzing && (
              <div className="animate-fade-in">
                
                <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                  
                  {/* Score Original */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, minWidth: '250px' }}>
                    <div style={{ 
                      width: '80px', height: '80px', 
                      borderRadius: '50%', 
                      background: `conic-gradient(var(--text-secondary) ${analysisResult.analise_ats.score_compatibilidade}%, var(--surface-color) 0)`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      boxShadow: 'var(--shadow-md)'
                    }}>
                      <div style={{ 
                        width: '64px', height: '64px', 
                        borderRadius: '50%', background: 'var(--bg-color)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: 'bold', fontSize: '1.25rem'
                      }}>
                        {analysisResult.analise_ats.score_compatibilidade}%
                      </div>
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1.1rem' }}>Score Original</h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        Baseado no currículo enviado.
                      </p>
                    </div>
                  </div>

                  {/* Score Otimizado */}
                  {analysisResult.analise_ats_otimizada && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, minWidth: '250px', background: 'rgba(16, 185, 129, 0.05)', padding: '1rem', borderRadius: '1rem', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                      <div style={{ 
                        width: '80px', height: '80px', 
                        borderRadius: '50%', 
                        background: `conic-gradient(#10b981 ${analysisResult.analise_ats_otimizada.score_compatibilidade}%, var(--surface-color) 0)`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: 'var(--shadow-md)'
                      }}>
                        <div style={{ 
                          width: '64px', height: '64px', 
                          borderRadius: '50%', background: 'var(--bg-color)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 'bold', fontSize: '1.25rem', color: '#10b981'
                        }}>
                          {analysisResult.analise_ats_otimizada.score_compatibilidade}%
                        </div>
                      </div>
                      <div>
                        <h3 style={{ fontSize: '1.1rem', color: '#10b981' }}>Novo Score Otimizado!</h3>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                          Aderência com o currículo reescrito.
                        </p>
                      </div>
                    </div>
                  )}

                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#10b981', marginBottom: '0.5rem' }}>
                    <CheckCircle size={18} /> Palavras-chave Encontradas
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {analysisResult.analise_ats.palavras_chave_encontradas.map((kw: string, i: number) => (
                      <span key={i} style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.875rem' }}>{kw}</span>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: '2rem' }}>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', marginBottom: '0.5rem' }}>
                    <AlertTriangle size={18} /> Palavras-chave Faltando (Gaps)
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {analysisResult.analise_ats.palavras_chave_faltando.map((gap: string, i: number) => (
                      <span key={i} style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.875rem' }}>{gap}</span>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: '2rem' }}>
                  <h4 style={{ marginBottom: '0.5rem' }}>💡 Dicas de Melhoria:</h4>
                  <ul style={{ listStylePosition: 'inside', paddingLeft: '1rem', color: 'var(--text-secondary)' }}>
                    {analysisResult.analise_ats.dicas_melhoria.map((dica: string, i: number) => <li key={i}>{dica}</li>)}
                  </ul>
                </div>

                <div style={{ background: 'var(--bg-color)', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid var(--border-color)', marginBottom: '1rem' }}>
                  <h4 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>Sua Nova Versão Otimizada</h4>
                  <p style={{ fontStyle: 'italic', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    {analysisResult.curriculo_otimizado.resumo_profissional}
                  </p>
                  
                  {analysisResult.curriculo_otimizado.experiencias.map((exp: any, i: number) => (
                    <div key={i} style={{ marginBottom: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                      <strong>{exp.cargo}</strong> - {exp.empresa} ({exp.periodo})
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>{exp.descricao}</p>
                    </div>
                  ))}
                </div>

                <div style={{ marginTop: '1rem' }}>
                  <PDFDownloadLink
                    document={<ResumePDFDocument data={analysisResult.curriculo_otimizado} />}
                    fileName="Curriculo_Otimizado_ATS.pdf"
                    style={{ textDecoration: 'none' }}
                  >
                    {({ loading }) => (
                      <div
                        style={{
                          padding: '0.75rem 1.5rem',
                          borderRadius: '0.5rem',
                          fontWeight: '600',
                          fontSize: '1rem',
                          cursor: loading ? 'not-allowed' : 'pointer',
                          background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                          color: '#fff',
                          boxShadow: 'var(--shadow-md)',
                          textAlign: 'center',
                          opacity: loading ? 0.7 : 1,
                        }}
                      >
                        {loading ? 'Preparando PDF...' : 'Baixar Currículo Otimizado (PDF Nativo)'}
                      </div>
                    )}
                  </PDFDownloadLink>
                </div>

              </div>
            )}
          </Card>
        </div>

      </div>
      )}
    </div>
  );
};
