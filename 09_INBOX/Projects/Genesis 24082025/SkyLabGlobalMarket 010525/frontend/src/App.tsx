import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Layouts
import { MainLayout } from '@components/layouts/MainLayout';
import { AuthLayout } from '@components/layouts/AuthLayout';

// Pages
import { Login } from '@pages/auth/Login';
import { Register } from '@pages/auth/Register';
import { Dashboard } from '@pages/dashboard/Dashboard';
import { Portfolio } from '@pages/portfolio/Portfolio';
import { Trading } from '@pages/trading/Trading';
import { Settings } from '@pages/settings/Settings';
import { NotFound } from '@pages/NotFound';

// Guards
import { AuthGuard } from '@components/guards/AuthGuard';
import { GuestGuard } from '@components/guards/GuestGuard';

const App: React.FC = () => {
  return (
    <>
      <Routes>
        {/* Rotas públicas */}
        <Route element={<GuestGuard />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>
        </Route>

        {/* Rotas protegidas */}
        <Route element={<AuthGuard />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        {/* Rota 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>

      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </>
  );
};

export default App; 