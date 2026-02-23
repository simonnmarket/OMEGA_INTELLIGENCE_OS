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
  Info as InfoIcon,
  ShowChart as ShowChartIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
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
  Info as InfoIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const FinancialControlDashboard = () => {
  const [financialData, setFinancialData] = useState({
    kpis: {
      totalProfit: 15000,
      totalVolume: 500000,
      riskExposure: 25,
      winRate: 65
    },
    operations: [
      {
        id: 1,
        symbol: 'EUR/USD',
        type: 'buy',
        volume: 1.0,
        price: 1.0850,
        status: 'executed',
        timestamp: '2024-03-01 10:15'
      },
      {
        id: 2,
        symbol: 'GBP/USD',
        type: 'sell',
        volume: 0.5,
        price: 1.2700,
        status: 'pending',
        timestamp: '2024-03-01 09:30'
      }
    ],
    bankAccounts: [
      {
        id: 1,
        name: 'Conta Principal',
        balance: 50000,
        currency: 'USD',
        lastUpdate: '2024-03-01 10:00'
      },
      {
        id: 2,
        name: 'Conta de Investimentos',
        balance: 25000,
        currency: 'EUR',
        lastUpdate: '2024-03-01 10:00'
      }
    ],
    alerts: [
      { id: 1, type: 'warning', message: 'Risco de exposição alto', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Nova operação executada', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedOperation, setSelectedOperation] = useState(null);
  const [showOperationDetails, setShowOperationDetails] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleReportDialog = () => {
    setShowReportDialog(true);
  };

  const handleCloseReportDialog = () => {
    setShowReportDialog(false);
  };

  const handleOperationClick = (operation) => {
    setSelectedOperation(operation);
    setShowOperationDetails(true);
  };

  const handleCloseOperationDetails = () => {
    setShowOperationDetails(false);
    setSelectedOperation(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'executed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
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
              Controle Financeiro
            </Typography>
            <Box>
              <Tooltip title="Gerar Relatório">
                <IconButton sx={{ mr: 1 }} onClick={handleReportDialog}>
                  <AssessmentIcon />
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
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Indicadores Principais"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Lucro Total
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    ${financialData.kpis.totalProfit}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Volume Total
                  </Typography>
                  <Typography variant="h4">
                    ${financialData.kpis.totalVolume}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Exposição ao Risco
                  </Typography>
                  <Typography variant="h4" color={financialData.kpis.riskExposure > 30 ? 'error.main' : 'warning.main'}>
                    {financialData.kpis.riskExposure}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Acerto
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {financialData.kpis.winRate}%
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Operações */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Operações Recentes"
              avatar={<ShowChartIcon />}
            />
            <CardContent>
              <List>
                {financialData.operations.map((operation) => (
                  <ListItem
                    key={operation.id}
                    button
                    onClick={() => handleOperationClick(operation)}
                    secondaryAction={
                      <Chip
                        label={operation.status}
                        color={getStatusColor(operation.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      {operation.type === 'buy' ? (
                        <TrendingUpIcon color="success" />
                      ) : (
                        <TrendingDownIcon color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={operation.symbol}
                      secondary={`Volume: ${operation.volume} | Preço: ${operation.price}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Contas Bancárias */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Contas Bancárias"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <List>
                {financialData.bankAccounts.map((account) => (
                  <ListItem
                    key={account.id}
                    secondaryAction={
                      <Typography variant="caption" color="text.secondary">
                        {account.lastUpdate}
                      </Typography>
                    }
                  >
                    <ListItemIcon>
                      <AttachMoneyIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={account.name}
                      secondary={`Saldo: ${account.balance} ${account.currency}`}
                    />
                  </ListItem>
                ))}
              </List>
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
                {financialData.alerts.map((alert) => (
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
      </Grid>

      {/* Diálogo de Detalhes da Operação */}
      <Dialog open={showOperationDetails} onClose={handleCloseOperationDetails} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes da Operação</DialogTitle>
        <DialogContent>
          {selectedOperation && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedOperation.symbol}</Typography>
              <Typography variant="body2" color="text.secondary">
                Tipo: {selectedOperation.type === 'buy' ? 'Compra' : 'Venda'}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Volume</Typography>
                  <Typography>{selectedOperation.volume}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Preço</Typography>
                  <Typography>{selectedOperation.price}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Status</Typography>
                  <Typography>{selectedOperation.status}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Data/Hora</Typography>
                  <Typography>{selectedOperation.timestamp}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseOperationDetails}>Fechar</Button>
          <Button onClick={handleCloseOperationDetails} variant="contained" color="error">
            Cancelar Operação
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialControlDashboard; 