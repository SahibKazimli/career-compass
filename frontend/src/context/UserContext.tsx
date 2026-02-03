import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import {
    User,
    getCurrentUser,
    login as apiLogin,
    register as apiRegister,
    logout as apiLogout,
    isAuthenticated as checkAuth,
    clearTokens,
    getAccessToken
} from '../services/api';

interface UserContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
    hasResume: boolean;
    setHasResume: (value: boolean) => void;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, name: string, password: string) => Promise<void>;
    logout: () => void;
    clearError: () => void;
    refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [hasResume, setHasResume] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Load user on mount if token exists
    useEffect(() => {
        const initAuth = async () => {
            if (checkAuth()) {
                try {
                    const userData = await getCurrentUser();
                    setUser(userData);
                    setIsAuthenticated(true);
                } catch (e) {
                    // Token invalid/expired, clear it
                    clearTokens();
                    setIsAuthenticated(false);
                }
            }
            setIsLoading(false);
        };
        initAuth();
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiLogin(email, password);
            const userData = await getCurrentUser();
            setUser(userData);
            setIsAuthenticated(true);
        } catch (e) {
            const errorMessage = e instanceof Error ? e.message : 'Failed to login';
            setError(errorMessage);
            throw e;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const register = useCallback(async (email: string, name: string, password: string) => {
        setIsLoading(true);
        setError(null);

        try {
            await apiRegister(email, name, password);
            const userData = await getCurrentUser();
            setUser(userData);
            setIsAuthenticated(true);
        } catch (e) {
            const errorMessage = e instanceof Error ? e.message : 'Failed to register';
            setError(errorMessage);
            throw e;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const logout = useCallback(() => {
        apiLogout();
        setUser(null);
        setHasResume(false);
        setIsAuthenticated(false);
    }, []);

    const refreshUser = useCallback(async () => {
        if (getAccessToken()) {
            try {
                const userData = await getCurrentUser();
                setUser(userData);
                setIsAuthenticated(true);
            } catch {
                logout();
            }
        }
    }, [logout]);

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    return (
        <UserContext.Provider
            value={{
                user,
                isLoading,
                isAuthenticated,
                error,
                hasResume,
                setHasResume,
                login,
                register,
                logout,
                clearError,
                refreshUser,
            }}
        >
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}
