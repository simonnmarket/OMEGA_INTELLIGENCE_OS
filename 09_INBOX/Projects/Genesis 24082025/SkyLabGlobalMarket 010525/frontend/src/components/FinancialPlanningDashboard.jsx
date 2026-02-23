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
  Info as InfoIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const FinancialPlanningDashboard = () => {
  const [financialData, setFinancialData] = useState({
    scenarios: [
      {
        id: 1,
        name: 'Cenário Conservador',
        status: 'active',
        progress: 60,
        metrics: {
          roi: 5.2,
          risk: 'Baixo',
          timeframe: '6 meses',
          confidence: 85
        },
        predictions: [
          { id: 1, metric: 'ROI', value: 5.2, trend: 'up', confidence: 85 },
          { id: 2, metric: 'Risco', value: 'Baixo', trend: 'stable', confidence: 90 },
          { id: 3, metric: 'Liquidez', value: 'Alta', trend: 'up', confidence: 80 }
        ],
        lastUpdate: '2024-03-01 10:00',
        logs: [
          { id: 1, timestamp: '2024-03-01 10:00', level: 'info', message: 'Cenário atualizado' },
          { id: 2, timestamp: '2024-03-01 09:30', level: 'success', message: 'Previsões recalculadas' },
          { id: 3, timestamp: '2024-03-01 09:15', level: 'warning', message: 'Ajuste necessário no risco' }
        ]
      }
    ],
    performanceMetrics: {
      totalScenarios: 8,
      activeScenarios: 3,
      averageROI: 4.8,
      riskLevel: 'Moderado',
      predictionAccuracy: 88
    },
    notifications: [
      { id: 1, type: 'warning', message: 'Cenário "Agressivo" requer revisão', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Novos dados disponíveis para análise', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewScenarioDialog, setShowNewScenarioDialog] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [showScenarioDetails, setShowScenarioDetails] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewScenarioDialog = () => {
    setShowNewScenarioDialog(true);
  };

  const handleCloseNewScenarioDialog = () => {
    setShowNewScenarioDialog(false);
  };

  const handleScenarioClick = (scenario) => {
    setSelectedScenario(scenario);
    setShowScenarioDetails(true);
  };

  const handleCloseScenarioDetails = () => {
    setShowScenarioDetails(false);
    setSelectedScenario(null);
  };

  const handleLogsClick = () => {
    setShowLogs(true);
  };

  const handleCloseLogs = () => {
    setShowLogs(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'primary';
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

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon color="success" />;
      case 'down':
        return <TrendingUpIcon color="error" style={{ transform: 'rotate(180deg)' }} />;
      case 'stable':
        return <TimelineIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Planejamento Financeiro
            </Typography>
            <Box>
              <Tooltip title="Novo Cenário">
                <IconButton sx={{ mr: 1 }} onClick={handleNewScenarioDialog}>
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

        {/* Métricas de Performance */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Métricas de Performance"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Total de Cenários
                  </Typography>
                  <Typography variant="h4">
                    {financialData.performanceMetrics.totalScenarios}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    ROI Médio
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {financialData.performanceMetrics.averageROI}%
                    </Typography>
                    <TrendingUpIcon color="success" />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Nível de Risco
                  </Typography>
                  <Typography variant="h4">
                    {financialData.performanceMetrics.riskLevel}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Precisão
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {financialData.performanceMetrics.predictionAccuracy}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={financialData.performanceMetrics.predictionAccuracy}
                      sx={{ width: 100 }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Cenários Ativos */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Cenários Ativos"
              avatar={<TimelineIcon />}
              action={
                <IconButton onClick={handleLogsClick}>
                  <HistoryIcon />
                </IconButton>
              }
            />
            <CardContent>
              {financialData.scenarios.map((scenario) => (
                <Accordion key={scenario.id} sx={{ mb: 2 }}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`scenario-${scenario.id}-content`}
                    id={`scenario-${scenario.id}-header`}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6">
                          {scenario.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Última atualização: {scenario.lastUpdate}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Chip
                          label={scenario.status}
                          color={getStatusColor(scenario.status)}
                          sx={{ mr: 2 }}
                        />
                        <LinearProgress
                          variant="determinate"
                          value={scenario.progress}
                          sx={{ width: 100 }}
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Métricas:
                        </Typography>
                        <List>
                          {scenario.predictions.map((prediction) => (
                            <ListItem key={prediction.id}>
                              <ListItemIcon>
                                {getTrendIcon(prediction.trend)}
                              </ListItemIcon>
                              <ListItemText
                                primary={prediction.metric}
                                secondary={`${prediction.value} (Confiança: ${prediction.confidence}%)`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Detalhes:
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2">
                            ROI: {scenario.metrics.roi}%
                          </Typography>
                          <Typography variant="body2">
                            Risco: {scenario.metrics.risk}
                          </Typography>
                          <Typography variant="body2">
                            Prazo: {scenario.metrics.timeframe}
                          </Typography>
                          <Typography variant="body2">
                            Confiança: {scenario.metrics.confidence}%
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Notificações */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Notificações"
              avatar={<NotificationsIcon />}
            />
            <CardContent>
              <List>
                {financialData.notifications.map((notification) => (
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
                        <CheckCircleIcon color="success" />
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

      {/* Diálogo de Detalhes do Cenário */}
      <Dialog open={showScenarioDetails} onClose={handleCloseScenarioDetails} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes do Cenário</DialogTitle>
        <DialogContent>
          {selectedScenario && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedScenario.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {selectedScenario.status}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2">Métricas:</Typography>
              <Box component={Paper} sx={{ p: 2, mt: 1 }}>
                <Code>
                  {JSON.stringify(selectedScenario.metrics, null, 2)}
                </Code>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseScenarioDetails}>Fechar</Button>
          <Button onClick={handleCloseScenarioDetails} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo de Logs */}
      <Dialog open={showLogs} onClose={handleCloseLogs} maxWidth="md" fullWidth>
        <DialogTitle>Logs do Cenário</DialogTitle>
        <DialogContent>
          <List>
            {financialData.scenarios[0].logs.map((log) => (
              <ListItem key={log.id}>
                <ListItemIcon>
                  {log.level === 'warning' ? (
                    <WarningIcon color="warning" />
                  ) : log.level === 'success' ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <InfoIcon color="info" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={log.message}
                  secondary={log.timestamp}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseLogs}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialPlanningDashboard; 