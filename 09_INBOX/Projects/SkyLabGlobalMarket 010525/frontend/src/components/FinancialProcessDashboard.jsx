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
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Receipt as ReceiptIcon,
  AccountBalance as AccountBalanceIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Description as DescriptionIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const FinancialProcessDashboard = () => {
  const [financialData, setFinancialData] = useState({
    accounting: {
      totalRevenue: 1500000,
      totalExpenses: 800000,
      netIncome: 700000,
      monthlyTrend: [
        { month: 'Jan', revenue: 120000, expenses: 65000 },
        { month: 'Fev', revenue: 130000, expenses: 70000 },
        { month: 'Mar', revenue: 140000, expenses: 75000 }
      ]
    },
    reports: [
      { id: 1, type: 'Balanço', date: '2024-03-01', status: 'completed' },
      { id: 2, type: 'DRE', date: '2024-03-01', status: 'pending' },
      { id: 3, type: 'Fluxo de Caixa', date: '2024-03-01', status: 'completed' }
    ],
    auditLogs: [
      { id: 1, action: 'Login', user: 'admin', timestamp: '2024-03-01 10:00', status: 'success' },
      { id: 2, action: 'Alteração de Dados', user: 'manager', timestamp: '2024-03-01 11:00', status: 'warning' },
      { id: 3, action: 'Exportação', user: 'analyst', timestamp: '2024-03-01 12:00', status: 'success' }
    ],
    kpis: {
      profitability: 46.7,
      liquidity: 1.8,
      efficiency: 0.85
    }
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState('');
  const [reportPeriod, setReportPeriod] = useState('');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleReportDialog = () => {
    setShowReportDialog(true);
  };

  const handleCloseReportDialog = () => {
    setShowReportDialog(false);
    setSelectedReportType('');
    setReportPeriod('');
  };

  const handleReportSubmit = () => {
    // TODO: Implementar geração de relatório
    handleCloseReportDialog();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Processos Financeiros
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

        {/* KPIs */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Indicadores Chave"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <BarChartIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Lucratividade"
                    secondary={`${financialData.kpis.profitability}%`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <TimelineIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Liquidez"
                    secondary={financialData.kpis.liquidity}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DescriptionIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Eficiência"
                    secondary={financialData.kpis.efficiency}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Contabilidade */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Contabilidade"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Receita Total
                  </Typography>
                  <Typography variant="h4">
                    ${financialData.accounting.totalRevenue.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Despesas
                  </Typography>
                  <Typography variant="h4" color="error">
                    ${financialData.accounting.totalExpenses.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Lucro Líquido
                  </Typography>
                  <Typography variant="h4" color="success">
                    ${financialData.accounting.netIncome.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={financialData.accounting.monthlyTrend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="revenue" stroke="#82ca9d" />
                        <Line type="monotone" dataKey="expenses" stroke="#ff7300" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Relatórios */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Relatórios"
              avatar={<DescriptionIcon />}
              action={
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleReportDialog}
                >
                  Novo Relatório
                </Button>
              }
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Data</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="right">Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {financialData.reports.map((report) => (
                      <TableRow key={report.id}>
                        <TableCell>{report.type}</TableCell>
                        <TableCell>{report.date}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={report.status}
                            color={getStatusColor(report.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Visualizar">
                            <IconButton size="small" sx={{ mr: 1 }}>
                              <DescriptionIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Exportar">
                            <IconButton size="small">
                              <ReceiptIcon />
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

        {/* Auditoria */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Logs de Auditoria"
              avatar={<SecurityIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Ação</TableCell>
                      <TableCell>Usuário</TableCell>
                      <TableCell>Data/Hora</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {financialData.auditLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>{log.action}</TableCell>
                        <TableCell>{log.user}</TableCell>
                        <TableCell>{log.timestamp}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={log.status}
                            color={getStatusColor(log.status)}
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

      {/* Diálogo de Novo Relatório */}
      <Dialog open={showReportDialog} onClose={handleCloseReportDialog}>
        <DialogTitle>Novo Relatório</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Tipo de Relatório</InputLabel>
            <Select
              value={selectedReportType}
              onChange={(e) => setSelectedReportType(e.target.value)}
              label="Tipo de Relatório"
            >
              <MenuItem value="balance">Balanço Patrimonial</MenuItem>
              <MenuItem value="dre">Demonstração de Resultados</MenuItem>
              <MenuItem value="cashflow">Fluxo de Caixa</MenuItem>
              <MenuItem value="custom">Personalizado</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Período</InputLabel>
            <Select
              value={reportPeriod}
              onChange={(e) => setReportPeriod(e.target.value)}
              label="Período"
            >
              <MenuItem value="daily">Diário</MenuItem>
              <MenuItem value="weekly">Semanal</MenuItem>
              <MenuItem value="monthly">Mensal</MenuItem>
              <MenuItem value="quarterly">Trimestral</MenuItem>
              <MenuItem value="yearly">Anual</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReportDialog}>Cancelar</Button>
          <Button onClick={handleReportSubmit} variant="contained">
            Gerar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialProcessDashboard; 