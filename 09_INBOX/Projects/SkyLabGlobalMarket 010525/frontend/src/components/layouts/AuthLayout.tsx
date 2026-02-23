import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container, CssBaseline, useTheme } from '@mui/material';
import { useAppSelector } from '@store/hooks';
import { selectSettings } from '@store/settings/settingsSlice';

export const AuthLayout: React.FC = () => {
  const theme = useTheme();
  const { settings } = useAppSelector(selectSettings);

  return (
    <Box
      sx={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default,
      }}
    >
      <CssBaseline />
      <Container
        maxWidth="sm"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          py: 4,
        }}
      >
        <Outlet />
      </Container>
    </Box>
  );
}; 