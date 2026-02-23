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
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const PortfolioManagementDashboard = () => {
  const [portfolioData, setPortfolioData] = useState({
    allocation: {
      forex: { target: 40, current: 38, change: -2 },
      indices: { target: 30, current: 32, change: +2 },
      commodities: { target: 20, current: 19, change: -1 },
      crypto: { target: 10, current: 11, change: +1 }
    },
    performance: {
      totalReturn: 12.5,
      sharpeRatio: 1.8,
      maxDrawdown: -5.2,
      winRate: 65
    },
    riskMetrics: {
      exposure: {
        forex: 38,
        indices: 32,
        commodities: 19,
        crypto: 11
      },
      correlation: {
        forexIndices: 0.45,
        forexCommodities: 0.32,
        indicesCommodities: 0.28
      },
      volatility: 15.2
    },
    scenarios: [
      {
        id: 1,
        name: 'Crise Econômica',
        impact: 'Alto',
        probability: 'Baixa',
        actions: ['Reduzir exposição em índices', 'Aumentar hedge em forex']
      },
      {
        id: 2,
        name: 'Volatilidade Alta',
        impact: 'Médio',
        probability: 'Média',
        actions: ['Ajustar stops dinâmicos', 'Reduzir alavancagem']
      }
    ],
    notifications: [
      { id: 1, type: 'warning', message: 'Alocação em Forex abaixo do target', timestamp: '2024-03-01 09:00' },
      { id: 2, type: 'info', message: 'Rebalanceamento automático agendado', timestamp: '2024-03-01 10:00' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showScenarioDialog, setShowScenarioDialog] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleScenarioClick = (scenario) => {
    setSelectedScenario(scenario);
    setShowScenarioDialog(true);
  };

  const handleCloseScenarioDialog = () => {
    setShowScenarioDialog(false);
    setSelectedScenario(null);
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'success';
    if (change < 0) return 'error';
    return 'default';
  };

  const getImpactColor = (impact) => {
    switch (impact.toLowerCase()) {
      case 'alto':
        return 'error';
      case 'médio':
        return 'warning';
      case 'baixo':
        return 'success';
      default:
        return 'default';
    }
  };

  const allocationData = Object.entries(portfolioData.allocation).map(([key, value]) => ({
    name: key.toUpperCase(),
    value: value.current
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Gestão de Portfólio
            </Typography>
            <Box>
              <Tooltip title="Rebalancear">
                <IconButton sx={{ mr: 1 }}>
                  <SyncIcon />
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

        {/* Alocação de Ativos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Alocação de Ativos"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={allocationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {allocationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              <List>
                {Object.entries(portfolioData.allocation).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      <AttachMoneyIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={key.toUpperCase()}
                      secondary={`Target: ${value.target}% | Atual: ${value.current}%`}
                    />
                    <Chip
                      label={`${value.change > 0 ? '+' : ''}${value.change}%`}
                      color={getChangeColor(value.change)}
                      size="small"
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
              avatar={<TrendingUpIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Retorno Total
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {portfolioData.performance.totalReturn}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Sharpe Ratio
                  </Typography>
                  <Typography variant="h4">
                    {portfolioData.performance.sharpeRatio}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Drawdown Máximo
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {portfolioData.performance.maxDrawdown}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Vitória
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {portfolioData.performance.winRate}%
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Métricas de Risco */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Métricas de Risco"
              avatar={<SecurityIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1">Exposição por Ativo</Typography>
                  {Object.entries(portfolioData.riskMetrics.exposure).map(([key, value]) => (
                    <Box key={key} sx={{ mb: 1 }}>
                      <Typography variant="body2">{key.toUpperCase()}</Typography>
                      <LinearProgress variant="determinate" value={value} />
                    </Box>
                  ))}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle1">Correlação</Typography>
                  {Object.entries(portfolioData.riskMetrics.correlation).map(([key, value]) => (
                    <Typography key={key} variant="body2">
                      {key.replace(/([A-Z])/g, ' $1').toUpperCase()}: {value}
                    </Typography>
                  ))}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle1">Volatilidade</Typography>
                  <Typography variant="h6">{portfolioData.riskMetrics.volatility}%</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Cenários */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Cenários"
              avatar={<PsychologyAltIcon />}
            />
            <CardContent>
              <List>
                {portfolioData.scenarios.map((scenario) => (
                  <ListItem
                    key={scenario.id}
                    button
                    onClick={() => handleScenarioClick(scenario)}
                  >
                    <ListItemIcon>
                      <PsychologyAltIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={scenario.name}
                      secondary={`Impacto: ${scenario.impact} | Probabilidade: ${scenario.probability}`}
                    />
                    <Chip
                      label={scenario.impact}
                      color={getImpactColor(scenario.impact)}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Notificações */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Notificações"
              avatar={<NotificationsIcon />}
            />
            <CardContent>
              <List>
                {portfolioData.notifications.map((notification) => (
                  <ListItem
                    key={notification.id}
                    secondaryAction={
                      <Typography variant="caption" color="text.secondary">
                        {notification.timestamp}
                      </Typography>
                    }
                  >
                    <ListItemIcon>
                      {notification.type === 'warning' ? (
                        <WarningIcon color="warning" />
                      ) : (
                        <InfoIcon color="info" />
                      )}
                    </ListItemIcon>
                    <ListItemText primary={notification.message} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Diálogo de Cenário */}
      <Dialog open={showScenarioDialog} onClose={handleCloseScenarioDialog} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes do Cenário</DialogTitle>
        <DialogContent>
          {selectedScenario && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedScenario.name}</Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Impacto</Typography>
                  <Chip
                    label={selectedScenario.impact}
                    color={getImpactColor(selectedScenario.impact)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Probabilidade</Typography>
                  <Typography>{selectedScenario.probability}</Typography>
                </Grid>
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2">Ações Recomendadas</Typography>
              <List>
                {selectedScenario.actions.map((action, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" />
                    </ListItemIcon>
                    <ListItemText primary={action} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseScenarioDialog}>Fechar</Button>
          <Button onClick={handleCloseScenarioDialog} variant="contained" color="primary">
            Aplicar Ações
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortfolioManagementDashboard; 