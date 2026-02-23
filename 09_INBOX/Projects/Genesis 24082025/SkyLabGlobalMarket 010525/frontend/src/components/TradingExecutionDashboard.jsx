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

const TradingExecutionDashboard = () => {
  const [tradingData, setTradingData] = useState({
    positions: [
      {
        id: 1,
        symbol: 'EUR/USD',
        type: 'buy',
        volume: 1.0,
        openPrice: 1.0850,
        currentPrice: 1.0875,
        profit: 25,
        status: 'open'
      },
      {
        id: 2,
        symbol: 'GBP/USD',
        type: 'sell',
        volume: 0.5,
        openPrice: 1.2700,
        currentPrice: 1.2680,
        profit: 10,
        status: 'open'
      }
    ],
    performance: {
      totalTrades: 150,
      winRate: 65,
      averageProfit: 15,
      totalProfit: 2250
    },
    alerts: [
      { id: 1, type: 'warning', message: 'Stop loss atingido em EUR/USD', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Nova posição aberta em GBP/USD', timestamp: '2024-03-01 09:30' }
    ],
    technicalIndicators: [
      {
        id: 1,
        name: 'RSI',
        value: 45,
        signal: 'neutral'
      },
      {
        id: 2,
        name: 'MACD',
        value: 0.0025,
        signal: 'buy'
      }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewPositionDialog, setShowNewPositionDialog] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [showPositionDetails, setShowPositionDetails] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewPositionDialog = () => {
    setShowNewPositionDialog(true);
  };

  const handleCloseNewPositionDialog = () => {
    setShowNewPositionDialog(false);
  };

  const handlePositionClick = (position) => {
    setSelectedPosition(position);
    setShowPositionDetails(true);
  };

  const handleClosePositionDetails = () => {
    setShowPositionDetails(false);
    setSelectedPosition(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'success';
      case 'closed':
        return 'default';
      case 'pending':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'buy':
        return 'success';
      case 'sell':
        return 'error';
      case 'neutral':
        return 'warning';
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
              Execução de Negociações
            </Typography>
            <Box>
              <Tooltip title="Nova Posição">
                <IconButton sx={{ mr: 1 }} onClick={handleNewPositionDialog}>
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

        {/* Posições Abertas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Posições Abertas"
              avatar={<ShowChartIcon />}
            />
            <CardContent>
              <List>
                {tradingData.positions.map((position) => (
                  <ListItem
                    key={position.id}
                    button
                    onClick={() => handlePositionClick(position)}
                    secondaryAction={
                      <Chip
                        label={position.status}
                        color={getStatusColor(position.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      {position.type === 'buy' ? (
                        <TrendingUpIcon color="success" />
                      ) : (
                        <TrendingDownIcon color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={position.symbol}
                      secondary={`Volume: ${position.volume} | Lucro: ${position.profit}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Desempenho */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Desempenho"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Total de Trades
                  </Typography>
                  <Typography variant="h4">
                    {tradingData.performance.totalTrades}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Acerto
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {tradingData.performance.winRate}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Lucro Médio
                  </Typography>
                  <Typography variant="h4">
                    ${tradingData.performance.averageProfit}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Lucro Total
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    ${tradingData.performance.totalProfit}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Indicadores Técnicos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Indicadores Técnicos"
              avatar={<AnalyticsIcon />}
            />
            <CardContent>
              <List>
                {tradingData.technicalIndicators.map((indicator) => (
                  <ListItem
                    key={indicator.id}
                    secondaryAction={
                      <Chip
                        label={indicator.signal}
                        color={getSignalColor(indicator.signal)}
                        size="small"
                      />
                    }
                  >
                    <ListItemText
                      primary={indicator.name}
                      secondary={`Valor: ${indicator.value}`}
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
                {tradingData.alerts.map((alert) => (
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

      {/* Diálogo de Detalhes da Posição */}
      <Dialog open={showPositionDetails} onClose={handleClosePositionDetails} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes da Posição</DialogTitle>
        <DialogContent>
          {selectedPosition && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedPosition.symbol}</Typography>
              <Typography variant="body2" color="text.secondary">
                Tipo: {selectedPosition.type === 'buy' ? 'Compra' : 'Venda'}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Volume</Typography>
                  <Typography>{selectedPosition.volume}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Preço de Abertura</Typography>
                  <Typography>{selectedPosition.openPrice}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Preço Atual</Typography>
                  <Typography>{selectedPosition.currentPrice}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Lucro</Typography>
                  <Typography color={selectedPosition.profit >= 0 ? 'success.main' : 'error.main'}>
                    {selectedPosition.profit}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePositionDetails}>Fechar</Button>
          <Button onClick={handleClosePositionDetails} variant="contained" color="error">
            Fechar Posição
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TradingExecutionDashboard; 