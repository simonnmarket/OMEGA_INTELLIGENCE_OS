import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Grid,
  Button,
  IconButton,
  Tooltip,
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  AvatarGroup,
  Divider,
  Paper,
  LinearProgress,
  Badge,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormControlLabel,
  Switch,
  Code,
  Terminal
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Group as GroupIcon,
  AutoAwesome as AutoAwesomeIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Share as ShareIcon,
  Notifications as NotificationsIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Assessment as AssessmentIcon,
  Chat as ChatIcon,
  Sync as SyncIcon,
  DragIndicator as DragIndicatorIcon,
  Api as ApiIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  History as HistoryIcon,
  IntegrationInstructions as IntegrationIcon,
  PsychologyAlt as PsychologyAltIcon,
  SmartToy as SmartToyIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Analytics as AnalyticsIcon,
  ShowChart as ShowChartIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  AccountBalance as AccountBalanceIcon,
  AttachMoney as AttachMoneyIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const LiquidityManagementDashboard = () => {
  const [liquidityData, setLiquidityData] = useState({
    cashPosition: {
      currentBalance: 1500000,
      availableBalance: 1200000,
      reservedBalance: 300000,
      currency: 'USD'
    },
    cashFlow: {
      forecast: [
        { date: '2024-03', amount: 1200000 },
        { date: '2024-04', amount: 1350000 },
        { date: '2024-05', amount: 1500000 },
        { date: '2024-06', amount: 1650000 }
      ],
      actual: [
        { date: '2024-01', amount: 900000 },
        { date: '2024-02', amount: 1050000 },
        { date: '2024-03', amount: 1200000 }
      ]
    },
    alerts: [
      { id: 1, type: 'warning', message: 'Saldo disponível abaixo do limite mínimo', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Novo fluxo de caixa previsto', timestamp: '2024-03-01 09:30' }
    ],
    reports: [
      {
        id: 1,
        name: 'Relatório Mensal',
        type: 'PDF',
        date: '2024-02-28',
        status: 'completed'
      },
      {
        id: 2,
        name: 'Análise de Liquidez',
        type: 'Excel',
        date: '2024-03-01',
        status: 'pending'
      }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewReportDialog, setShowNewReportDialog] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showReportDetails, setShowReportDetails] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewReportDialog = () => {
    setShowNewReportDialog(true);
  };

  const handleCloseNewReportDialog = () => {
    setShowNewReportDialog(false);
  };

  const handleReportClick = (report) => {
    setSelectedReport(report);
    setShowReportDetails(true);
  };

  const handleCloseReportDetails = () => {
    setShowReportDetails(false);
    setSelectedReport(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: liquidityData.cashPosition.currency
    }).format(amount);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Gestão de Liquidez
            </Typography>
            <Box>
              <Tooltip title="Novo Relatório">
                <IconButton sx={{ mr: 1 }} onClick={handleNewReportDialog}>
                  <AddIcon />
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

        {/* Posição de Caixa */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Posição de Caixa"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  Saldo Atual
                </Typography>
                <Typography variant="h4">
                  {formatCurrency(liquidityData.cashPosition.currentBalance)}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" color="text.secondary">
                  Saldo Disponível
                </Typography>
                <Typography variant="h4" color="success.main">
                  {formatCurrency(liquidityData.cashPosition.availableBalance)}
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="text.secondary">
                  Saldo Reservado
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {formatCurrency(liquidityData.cashPosition.reservedBalance)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Fluxo de Caixa */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Fluxo de Caixa"
              avatar={<AttachMoneyIcon />}
            />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={liquidityData.cashFlow.forecast}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="amount"
                      stroke="#8884d8"
                      name="Previsão"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Alertas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Alertas"
              avatar={<WarningIcon />}
            />
            <CardContent>
              <List>
                {liquidityData.alerts.map((alert) => (
                  <ListItem
                    key={alert.id}
                    secondaryAction={
                      <Typography variant="caption" color="text.secondary">
                        {alert.timestamp}
                      </Typography>
                    }
                  >
                    <ListItemIcon>
                      {alert.type === 'warning' ? (
                        <WarningIcon color="warning" />
                      ) : (
                        <CheckCircleIcon color="success" />
                      )}
                    </ListItemIcon>
                    <ListItemText primary={alert.message} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Relatórios */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Relatórios"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <List>
                {liquidityData.reports.map((report) => (
                  <ListItem
                    key={report.id}
                    button
                    onClick={() => handleReportClick(report)}
                    secondaryAction={
                      <Chip
                        label={report.status}
                        color={getStatusColor(report.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      {report.type === 'PDF' ? (
                        <PictureAsPdfIcon />
                      ) : (
                        <TableChartIcon />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={report.name}
                      secondary={report.date}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Diálogo de Detalhes do Relatório */}
      <Dialog open={showReportDetails} onClose={handleCloseReportDetails} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes do Relatório</DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedReport.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Data: {selectedReport.date}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2">Tipo: {selectedReport.type}</Typography>
              <Typography variant="subtitle2">Status: {selectedReport.status}</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReportDetails}>Fechar</Button>
          <Button onClick={handleCloseReportDetails} variant="contained">
            Exportar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LiquidityManagementDashboard; 