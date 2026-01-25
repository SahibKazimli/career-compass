import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Resume from "./pages/Resume";
import Roadmap from "./pages/Roadmap";
import Skills from "./pages/Skills";
import Resources from "./pages/Resources";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
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
            path="/roadmap"
            element={
              <DashboardLayout>
                <Roadmap />
              </DashboardLayout>
            }
          />
          <Route
            path="/skills"
            element={
              <DashboardLayout>
                <Skills />
              </DashboardLayout>
            }
          />
          <Route
            path="/resources"
            element={
              <DashboardLayout>
                <Resources />
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
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
