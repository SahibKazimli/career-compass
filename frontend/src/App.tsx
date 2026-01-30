import { Toaster } from 'sonner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import { DashboardLayout } from './components/layout/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Resume from './pages/Resume';

import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient();

const App = () => (
    <QueryClientProvider client={queryClient}>
        <UserProvider>
            {/* Configure Sonner toaster at the root */}
            <Toaster position="top-right" closeButton richColors />
            <BrowserRouter>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <DashboardLayout>
                                <Dashboard />
                            </DashboardLayout>
                        }
                    />
                    <Route
                        path="/resume"
                        element={
                            <DashboardLayout>
                                <Resume />
                            </DashboardLayout>
                        }
                    />

                    <Route
                        path="/settings"
                        element={
                            <DashboardLayout>
                                <Settings />
                            </DashboardLayout>
                        }
                    />
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </BrowserRouter>
        </UserProvider>
    </QueryClientProvider>
);

export default App;
