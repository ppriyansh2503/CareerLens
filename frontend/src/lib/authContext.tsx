import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from './types';
import { authAPI, setAuthToken } from './api';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<UserRole>;
  register: (userData: any) => Promise<any>;
  logout: () => void;
  switchRole: (role: 'student' | 'recruiter' | 'college_admin') => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('careerlens_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async () => {
    try {
      const userData = await authAPI.me();
      setUser(userData);
      setRole(userData.role);
    } catch (err) {
      console.warn('Session verification failed, logging out');
      setAuthToken(null);
      setUser(null);
      setRole(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, pass: string): Promise<UserRole> => {
    setIsLoading(true);
    try {
      const data = await authAPI.login(email, pass);
      setAuthToken(data.access_token);
      setToken(data.access_token);
      setRole(data.role);
      
      const userData = await authAPI.me();
      setUser(userData);
      return data.role;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: any): Promise<any> => {
    setIsLoading(true);
    try {
      const data = await authAPI.register(userData);
      if (data.approval_status === "APPROVED" && data.access_token) {
        setAuthToken(data.access_token);
        setToken(data.access_token);
        setRole(data.role);
        const meData = await authAPI.me();
        setUser(meData);
      } else {
        // Newly registered accounts start in PENDING and require admin approval
        setAuthToken(null);
        setToken(null);
        setRole(null);
        setUser(null);
      }
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setUser(null);
    setToken(null);
    setRole(null);
  };

  const switchRole = async (targetRole: 'student' | 'recruiter' | 'college_admin') => {
    setIsLoading(true);
    try {
      const data = await authAPI.demoSwitch(targetRole);
      setAuthToken(data.access_token);
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
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        switchRole
      }}
    >
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
