import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from './types';
import { authAPI } from './api';

interface AuthContextType {
  user: User | null;
  role: UserRole;
  token: string | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: 'student' | 'recruiter' | 'college_admin') => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>('student');
  const [token, setToken] = useState<string | null>(localStorage.getItem('careerlens_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async () => {
    try {
      const userData = await authAPI.me();
      setUser(userData);
      setRole(userData.role);
    } catch (err) {
      console.warn('Auto login failed or token expired, auto-switching to demo student');
      await switchRole('student');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      // Default to demo student for friction-free judge experience!
      switchRole('student');
    }
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const data = await authAPI.login(email, pass);
      localStorage.setItem('careerlens_token', data.access_token);
      setToken(data.access_token);
      setRole(data.role);
      await fetchCurrentUser();
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('careerlens_token');
    setUser(null);
    setToken(null);
    setRole('student');
  };

  const switchRole = async (targetRole: 'student' | 'recruiter' | 'college_admin') => {
    setIsLoading(true);
    try {
      const data = await authAPI.demoSwitch(targetRole);
      localStorage.setItem('careerlens_token', data.access_token);
      setToken(data.access_token);
      setRole(data.role);
      const userData = await authAPI.me();
      setUser(userData);
    } catch (err) {
      console.error('Failed to switch demo role:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, role, token, isLoading, login, logout, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
