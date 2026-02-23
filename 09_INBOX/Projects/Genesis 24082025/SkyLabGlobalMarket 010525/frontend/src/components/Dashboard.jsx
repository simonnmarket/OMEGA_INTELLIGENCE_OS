import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
  Warning as WarningIcon,
  Notifications as NotificationsIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Calculate as CalculateIcon,
  Verified as VerifiedIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area } from 'recharts';

const Dashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    balance: 0,
    equity: 0,
    margin: 0,
    freeMargin: 0,
    marginLevel: 0
  });

  const [performanceData, setPerformanceData] = useState([]);
  const [activePositions, setActivePositions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState('');
  const [complianceStatus, setComplianceStatus] = useState({
    riskLevel: 'medium',
    lastAudit: new Date().toISOString(),
    violations: 0,
    checks: [
      { name: 'Validação de Transações', status: 'passed', timestamp: new Date().toISOString() },
      { name: 'Conformidade Regulatória', status: 'pending', timestamp: new Date().toISOString() },
      { name: 'Limites de Risco', status: 'passed', timestamp: new Date().toISOString() }
    ]
  });

  const [waterfallData, setWaterfallData] = useState([
    { name: 'Retorno Total', value: 100000 },
    { name: 'Taxa de Gestão', value: 2000 },
    { name: 'Carried Interest', value: 8000 },
    { name: 'Retorno Líquido', value: 90000 }
  ]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // TODO: Implementar chamadas reais à API
        setPortfolioData({
          balance: 100000,
          equity: 105000,
          margin: 5000,
          freeMargin: 95000,
          marginLevel: 2100
        });

        setPerformanceData([
          { date: '2024-01', value: 100000, risk: 0.2, compliance: 0.9 },
          { date: '2024-02', value: 102000, risk: 0.3, compliance: 0.85 },
          { date: '2024-03', value: 105000, risk: 0.25, compliance: 0.95 }
        ]);

        setActivePositions([
          { symbol: 'EURUSD', type: 'buy', volume: 0.1, price: 1.08, profit: 50, risk: 0.2, compliance: 'passed' },
          { symbol: 'GBPUSD', type: 'sell', volume: 0.05, price: 1.25, profit: -25, risk: 0.3, compliance: 'pending' }
        ]);

        setAlerts([
          { type: 'warning', message: 'Alto risco detectado em EURUSD' },
          { type: 'info', message: 'Nova estratégia disponível' },
          { type: 'success', message: 'Auditoria de conformidade concluída' },
          { type: 'error', message: 'Violação de limite de risco detectada' }
        ]);

        setLoading(false);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    // TODO: Implementar atualização de dados
    setTimeout(() => setLoading(false), 1000);
  };

  const handleGenerateReport = () => {
    setShowReportDialog(true);
  };

  const handleCloseReportDialog = () => {
    setShowReportDialog(false);
  };

  const handleReportTypeChange = (event) => {
    setSelectedReportType(event.target.value);
  };

  const getComplianceStatusColor = (status) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Dashboard
            </Typography>
            <Box>
              <Tooltip title="Gerar Relatório">
                <Button
                  variant="contained"
                  startIcon={<AssessmentIcon />}
                  onClick={handleGenerateReport}
                  sx={{ mr: 2 }}
                >
                  Relatório
                </Button>
              </Tooltip>
              <Tooltip title="Atualizar dados">
                <IconButton onClick={handleRefresh} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Grid>

        {/* Alertas */}
        <Grid item xs={12}>
          {alerts.map((alert, index) => (
            <Alert key={index} severity={alert.type} sx={{ mb: 1 }}>
              {alert.message}
            </Alert>
          ))}
        </Grid>

        {/* Resumo do Portfólio */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Resumo do Portfólio"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <AccountBalanceIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Saldo"
                    secondary={`$${portfolioData.balance.toLocaleString()}`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUpIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Equity"
                    secondary={`$${portfolioData.equity.toLocaleString()}`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Nível de Margem"
                    secondary={`${portfolioData.marginLevel}%`}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Status de Conformidade */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Status de Conformidade"
              avatar={<SecurityIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Verificação</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="right">Data</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {complianceStatus.checks.map((check, index) => (
                      <TableRow key={index}>
                        <TableCell>{check.name}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={check.status}
                            color={getComplianceStatusColor(check.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          {new Date(check.timestamp).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Waterfall Calculations */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Cálculos de Distribuição"
              avatar={<CalculateIcon />}
            />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={waterfallData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <ChartTooltip />
                    <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance e Risco */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Performance e Risco"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                    <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                    <ChartTooltip />
                    <Bar yAxisId="left" dataKey="value" fill="#8884d8" />
                    <Bar yAxisId="right" dataKey="risk" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Posições Ativas */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Posições Ativas"
              avatar={<NotificationsIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Ativo</TableCell>
                      <TableCell align="right">Tipo</TableCell>
                      <TableCell align="right">Volume</TableCell>
                      <TableCell align="right">Preço</TableCell>
                      <TableCell align="right">Lucro</TableCell>
                      <TableCell align="right">Risco</TableCell>
                      <TableCell align="right">Conformidade</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activePositions.map((position, index) => (
                      <TableRow key={index}>
                        <TableCell>{position.symbol}</TableCell>
                        <TableCell align="right">{position.type.toUpperCase()}</TableCell>
                        <TableCell align="right">{position.volume}</TableCell>
                        <TableCell align="right">{position.price}</TableCell>
                        <TableCell align="right">${position.profit}</TableCell>
                        <TableCell align="right">{position.risk}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={position.compliance}
                            color={getComplianceStatusColor(position.compliance)}
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
      </Grid>

      {/* Diálogo de Relatório */}
      <Dialog open={showReportDialog} onClose={handleCloseReportDialog}>
        <DialogTitle>Gerar Relatório</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Tipo de Relatório</InputLabel>
            <Select
              value={selectedReportType}
              onChange={handleReportTypeChange}
              label="Tipo de Relatório"
            >
              <MenuItem value="performance">Performance</MenuItem>
              <MenuItem value="risk">Análise de Risco</MenuItem>
              <MenuItem value="compliance">Conformidade</MenuItem>
              <MenuItem value="positions">Posições Ativas</MenuItem>
              <MenuItem value="waterfall">Cálculos de Distribuição</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReportDialog}>Cancelar</Button>
          <Button onClick={handleCloseReportDialog} variant="contained">
            Gerar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard; 