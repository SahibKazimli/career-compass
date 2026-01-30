import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { User, getUserByEmail, createUser, getUserById } from '../services/api';

interface UserContextType {
    user: User | null;
    isLoading: boolean;
    error: string | null;
    hasResume: boolean;
    setHasResume: (value: boolean) => void;
    login: (email: string, name: string) => Promise<void>;
    loginWithId: (userId: number) => Promise<void>;
    logout: () => void;
    clearError: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const USER_STORAGE_KEY = 'career_compass_user';

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [hasResume, setHasResume] = useState(false);

    // Load user from localStorage on mount
    useEffect(() => {
        const savedUser = localStorage.getItem(USER_STORAGE_KEY);
        if (savedUser) {
            try {
                const parsed = JSON.parse(savedUser);
                setUser(parsed);
            } catch (e) {
                localStorage.removeItem(USER_STORAGE_KEY);
            }
        }
        setIsLoading(false);
    }, []);

    // Save user to localStorage when it changes
    useEffect(() => {
        if (user) {
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
        } else {
            localStorage.removeItem(USER_STORAGE_KEY);
        }
    }, [user]);

    const login = useCallback(async (email: string, name: string) => {
        setIsLoading(true);
        setError(null);

        try {
            // Try to get existing user
            let userData: User;
            try {
                userData = await getUserByEmail(email);
            } catch (e) {
                // User doesn't exist, create new one
                userData = await createUser(email, name);
            }
            setUser(userData);
        } catch (e) {
            const errorMessage = e instanceof Error ? e.message : 'Failed to login';
            setError(errorMessage);
            throw e;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const loginWithId = useCallback(async (userId: number) => {
        setIsLoading(true);
        setError(null);

        try {
            const userData = await getUserById(userId);
            setUser(userData);
        } catch (e) {
            const errorMessage = e instanceof Error ? e.message : 'Failed to login';
            setError(errorMessage);
            throw e;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const logout = useCallback(() => {
        setUser(null);
        setHasResume(false);
        localStorage.removeItem(USER_STORAGE_KEY);
    }, []);

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    return (
        <UserContext.Provider
            value={{
                user,
                isLoading,
                error,
                hasResume,
                setHasResume,
                login,
                loginWithId,
                logout,
                clearError,
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
