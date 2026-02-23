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
  InputLabel
} from '@mui/material';
import {
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ReconciliationDashboard = () => {
  const [reconciliationData, setReconciliationData] = useState({
    status: 'processing',
    lastSync: new Date().toISOString(),
    transactions: [],
    discrepancies: [],
    sources: [
      { name: 'MetaTrader 5', status: 'connected', lastSync: new Date().toISOString() },
      { name: 'Banco Principal', status: 'connected', lastSync: new Date().toISOString() },
      { name: 'Corretora', status: 'pending', lastSync: new Date().toISOString() }
    ]
  });

  const [showSettings, setShowSettings] = useState(false);
  const [selectedSource, setSelectedSource] = useState('');
  const [syncStatus, setSyncStatus] = useState('idle');

  useEffect(() => {
    // Simular carregamento de dados
    const fetchData = async () => {
      try {
        // TODO: Implementar chamadas reais à API
        setReconciliationData(prev => ({
          ...prev,
          transactions: [
            { id: 1, date: '2024-03-01', amount: 1000, source: 'MT5', status: 'matched' },
            { id: 2, date: '2024-03-01', amount: 1000, source: 'Bank', status: 'matched' },
            { id: 3, date: '2024-03-01', amount: 500, source: 'MT5', status: 'unmatched' },
            { id: 4, date: '2024-03-01', amount: 500, source: 'Broker', status: 'pending' }
          ],
          discrepancies: [
            { id: 1, type: 'amount', source1: 'MT5', source2: 'Bank', amount: 100, date: '2024-03-01' },
            { id: 2, type: 'missing', source: 'Broker', amount: 500, date: '2024-03-01' }
          ]
        }));
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };

    fetchData();
  }, []);

  const handleSync = async () => {
    setSyncStatus('syncing');
    // TODO: Implementar sincronização real
    setTimeout(() => {
      setSyncStatus('idle');
      setReconciliationData(prev => ({
        ...prev,
        lastSync: new Date().toISOString()
      }));
    }, 2000);
  };

  const handleSettings = () => {
    setShowSettings(true);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'matched':
        return 'success';
      case 'unmatched':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'matched':
        return <CheckCircleIcon color="success" />;
      case 'unmatched':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <WarningIcon color="warning" />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Reconciliação Financeira
            </Typography>
            <Box>
              <Tooltip title="Configurações">
                <IconButton onClick={handleSettings} sx={{ mr: 1 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Sincronizar">
                <IconButton onClick={handleSync} disabled={syncStatus === 'syncing'}>
                  {syncStatus === 'syncing' ? <CircularProgress size={24} /> : <SyncIcon />}
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          <Alert severity="info" sx={{ mb: 2 }}>
            Última sincronização: {new Date(reconciliationData.lastSync).toLocaleString()}
          </Alert>
        </Grid>

        {/* Status das Fontes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Status das Fontes"
              avatar={<SyncIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Fonte</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="right">Última Sincronização</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {reconciliationData.sources.map((source, index) => (
                      <TableRow key={index}>
                        <TableCell>{source.name}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={source.status}
                            color={getStatusColor(source.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          {new Date(source.lastSync).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Discrepâncias */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Discrepâncias Detectadas"
              avatar={<WarningIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell align="right">Valor</TableCell>
                      <TableCell align="right">Data</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {reconciliationData.discrepancies.map((discrepancy, index) => (
                      <TableRow key={index}>
                        <TableCell>{discrepancy.type}</TableCell>
                        <TableCell align="right">${discrepancy.amount}</TableCell>
                        <TableCell align="right">{discrepancy.date}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label="Pendente"
                            color="warning"
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Transações */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Transações"
              avatar={<SyncIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Data</TableCell>
                      <TableCell align="right">Valor</TableCell>
                      <TableCell>Fonte</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="right">Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {reconciliationData.transactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>{transaction.date}</TableCell>
                        <TableCell align="right">${transaction.amount}</TableCell>
                        <TableCell>{transaction.source}</TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                            {getStatusIcon(transaction.status)}
                            <Chip
                              label={transaction.status}
                              color={getStatusColor(transaction.status)}
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Resolver">
                            <IconButton size="small">
                              <SyncIcon />
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

      {/* Diálogo de Configurações */}
      <Dialog open={showSettings} onClose={handleCloseSettings}>
        <DialogTitle>Configurações de Reconciliação</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Fonte de Dados</InputLabel>
            <Select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              label="Fonte de Dados"
            >
              <MenuItem value="mt5">MetaTrader 5</MenuItem>
              <MenuItem value="bank">Banco Principal</MenuItem>
              <MenuItem value="broker">Corretora</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Intervalo de Sincronização (minutos)"
            type="number"
            defaultValue="15"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSettings}>Cancelar</Button>
          <Button onClick={handleCloseSettings} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ReconciliationDashboard; 