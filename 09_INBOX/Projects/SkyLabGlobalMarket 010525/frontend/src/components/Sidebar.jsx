import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Divider,
  ListItemButton
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as PortfolioIcon,
  Assessment as RiskIcon,
  TrendingUp as TradingIcon,
  Description as ReportsIcon,
  Settings as SettingsIcon,
  ExitToApp as LogoutIcon
} from '@mui/icons-material';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Gestão de Portfólio', icon: <PortfolioIcon />, path: '/portfolio' },
  { text: 'Análise de Risco', icon: <RiskIcon />, path: '/risk' },
  { text: 'Execução de Operações', icon: <TradingIcon />, path: '/trading' },
  { text: 'Relatórios', icon: <ReportsIcon />, path: '/reports' },
  { text: 'Configurações', icon: <SettingsIcon />, path: '/settings' }
];

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box
      sx={{
        width: 250,
        height: '100vh',
        backgroundColor: '#f4f6f8',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="primary">
          SKY LAB GLOBAL MARKET
        </Typography>
      </Box>

      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar sx={{ width: 40, height: 40 }}>U</Avatar>
        <Box>
          <Typography variant="subtitle1">Usuário</Typography>
          <Typography variant="body2" color="text.secondary">
            admin@skylab.com
          </Typography>
        </Box>
      </Box>

      <Divider />

      <List sx={{ flex: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate('/logout')}>
            <ListItemIcon>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Sair" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};

export default Sidebar; 