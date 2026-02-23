import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  Timeline as TimelineIcon,
  Security as SecurityIcon,
  AttachMoney as AttachMoneyIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Remove as RemoveIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const FundManagementDashboard = () => {
  const [fundData, setFundData] = useState({
    totalBalance: 1000000,
    performance: {
      daily: 2.5,
      weekly: 5.8,
      monthly: 12.3,
      yearly: 45.6
    },
    riskExposure: {
      high: 15,
      medium: 30,
      low: 55
    },
    cashFlow: [
      { date: '2024-03-01', inflow: 50000, outflow: 30000 },
      { date: '2024-03-02', inflow: 45000, outflow: 35000 },
      { date: '2024-03-03', inflow: 60000, outflow: 40000 }
    ],
    pendingOrders: [
      { id: 1, type: 'BUY', symbol: 'EURUSD', amount: 10000, status: 'pending' },
      { id: 2, type: 'SELL', symbol: 'GBPUSD', amount: 5000, status: 'approved' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showOrderDialog, setShowOrderDialog] = useState(false);
  const [newOrder, setNewOrder] = useState({
    type: '',
    symbol: '',
    amount: '',
    reason: ''
  });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleOrderDialog = () => {
    setShowOrderDialog(true);
  };

  const handleCloseOrderDialog = () => {
    setShowOrderDialog(false);
    setNewOrder({
      type: '',
      symbol: '',
      amount: '',
      reason: ''
    });
  };

  const handleOrderSubmit = () => {
    // TODO: Implementar submissão de ordem
    handleCloseOrderDialog();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Gestão de Fundos
            </Typography>
            <Box>
              <Tooltip title="Configurações">
                <IconButton sx={{ mr: 1 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Atualizar">
                <IconButton>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Grid>

        {/* Resumo do Fundo */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Saldo Total"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <Typography variant="h4" component="div" sx={{ mb: 2 }}>
                ${fundData.totalBalance.toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Diário: +{fundData.performance.daily}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Mensal: +{fundData.performance.monthly}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Exposição ao Risco */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Exposição ao Risco"
              avatar={<SecurityIcon />}
            />
            <CardContent>
              <Box sx={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { name: 'Alto', value: fundData.riskExposure.high },
                    { name: 'Médio', value: fundData.riskExposure.medium },
                    { name: 'Baixo', value: fundData.riskExposure.low }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Fluxo de Caixa */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Fluxo de Caixa"
              avatar={<AttachMoneyIcon />}
            />
            <CardContent>
              <Box sx={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={fundData.cashFlow}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="inflow" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="outflow" stroke="#ff7300" />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Ordens Pendentes */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Ordens Pendentes"
              action={
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOrderDialog}
                >
                  Nova Ordem
                </Button>
              }
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Ativo</TableCell>
                      <TableCell align="right">Valor</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="right">Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {fundData.pendingOrders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell>
                          {order.type === 'BUY' ? (
                            <AddIcon color="success" />
                          ) : (
                            <RemoveIcon color="error" />
                          )}
                        </TableCell>
                        <TableCell>{order.symbol}</TableCell>
                        <TableCell align="right">${order.amount.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={order.status}
                            color={getStatusColor(order.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Aprovar">
                            <IconButton size="small" sx={{ mr: 1 }}>
                              <CheckCircleIcon color="success" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Rejeitar">
                            <IconButton size="small">
                              <ErrorIcon color="error" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Diálogo de Nova Ordem */}
      <Dialog open={showOrderDialog} onClose={handleCloseOrderDialog}>
        <DialogTitle>Nova Ordem</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Tipo</InputLabel>
            <Select
              value={newOrder.type}
              onChange={(e) => setNewOrder({ ...newOrder, type: e.target.value })}
              label="Tipo"
            >
              <MenuItem value="BUY">Compra</MenuItem>
              <MenuItem value="SELL">Venda</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Ativo"
            value={newOrder.symbol}
            onChange={(e) => setNewOrder({ ...newOrder, symbol: e.target.value })}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="Valor"
            type="number"
            value={newOrder.amount}
            onChange={(e) => setNewOrder({ ...newOrder, amount: e.target.value })}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="Motivo"
            multiline
            rows={4}
            value={newOrder.reason}
            onChange={(e) => setNewOrder({ ...newOrder, reason: e.target.value })}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseOrderDialog}>Cancelar</Button>
          <Button onClick={handleOrderSubmit} variant="contained">
            Enviar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FundManagementDashboard; 