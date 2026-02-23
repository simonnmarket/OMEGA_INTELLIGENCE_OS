import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import { Warning as WarningIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchRiskMetrics } from '../store/riskSlice';

const RiskAnalysis = () => {
  const dispatch = useDispatch();
  const { metrics, loading } = useSelector(state => state.risk);

  useEffect(() => {
    dispatch(fetchRiskMetrics());
  }, [dispatch]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Análise de Risco
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Métricas de Risco
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Exposição ao Risco"
                  secondary={`${metrics.riskExposure}%`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Correlação Média"
                  secondary={metrics.correlation}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Risco de Cenários Adversos"
                  secondary={`${metrics.adverseRisk}%`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Value at Risk (VaR)"
                  secondary={`${metrics.var}%`}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Alertas de Risco
            </Typography>
            <List>
              {metrics.alerts.map((alert, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {alert.severity === 'high' ? (
                      <WarningIcon color="error" />
                    ) : (
                      <CheckCircleIcon color="success" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.message}
                    secondary={alert.details}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Distribuição de Risco por Ativo
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.riskDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="asset" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="risk" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskAnalysis; 