import React, { useState, useEffect } from 'react';
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
  Storage as StorageIcon
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ProcessAutomationDashboard = () => {
  const [processData, setProcessData] = useState({
    activeProcesses: [
      {
        id: 1,
        name: 'Análise e Execução de Ordens',
        status: 'running',
        progress: 75,
        steps: [
          { id: 1, name: 'Coleta de Dados', status: 'completed', type: 'API', config: { source: 'MetaTrader 5' } },
          { id: 2, name: 'Análise de Risco', status: 'running', type: 'IA', config: { model: 'TensorFlow' } },
          { id: 3, name: 'Execução de Ordens', status: 'pending', type: 'EA', config: { platform: 'MetaTrader 5' } }
        ],
        integrations: [
          { id: 1, name: 'MetaTrader 5', status: 'active', type: 'Trading' },
          { id: 2, name: 'API Financeira', status: 'active', type: 'Dados' },
          { id: 3, name: 'TensorFlow', status: 'active', type: 'IA' }
        ],
        lastUpdate: '2024-03-01 10:00',
        metrics: {
          efficiency: 85,
          accuracy: 92,
          speed: '2s'
        },
        logs: [
          { id: 1, timestamp: '2024-03-01 10:00', level: 'info', message: 'Processo iniciado' },
          { id: 2, timestamp: '2024-03-01 10:01', level: 'success', message: 'Coleta de dados concluída' },
          { id: 3, timestamp: '2024-03-01 10:02', level: 'warning', message: 'Análise de risco em andamento' }
        ]
      }
    ],
    performanceMetrics: {
      totalProcesses: 15,
      activeProcesses: 8,
      successRate: 92,
      averageTime: '2.5h',
      efficiency: 85,
      accuracy: 92
    },
    notifications: [
      { id: 1, type: 'warning', message: 'Processo "Análise e Execução" está atrasado', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Nova integração disponível: Alpha Vantage', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewProcessDialog, setShowNewProcessDialog] = useState(false);
  const [selectedStep, setSelectedStep] = useState(null);
  const [showStepConfig, setShowStepConfig] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewProcessDialog = () => {
    setShowNewProcessDialog(true);
  };

  const handleCloseNewProcessDialog = () => {
    setShowNewProcessDialog(false);
  };

  const handleStepClick = (step) => {
    setSelectedStep(step);
    setShowStepConfig(true);
  };

  const handleCloseStepConfig = () => {
    setShowStepConfig(false);
    setSelectedStep(null);
  };

  const handleLogsClick = () => {
    setShowLogs(true);
  };

  const handleCloseLogs = () => {
    setShowLogs(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
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

  const getStepIcon = (type) => {
    switch (type) {
      case 'IA':
        return <PsychologyAltIcon />;
      case 'EA':
        return <SmartToyIcon />;
      case 'API':
        return <ApiIcon />;
      default:
        return <AutoAwesomeIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Automação de Processos
            </Typography>
            <Box>
              <Tooltip title="Novo Processo">
                <IconButton sx={{ mr: 1 }} onClick={handleNewProcessDialog}>
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
                    Total de Processos
                  </Typography>
                  <Typography variant="h4">
                    {processData.performanceMetrics.totalProcesses}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Sucesso
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {processData.performanceMetrics.successRate}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={processData.performanceMetrics.successRate}
                      sx={{ width: 100 }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Processos Ativos
                  </Typography>
                  <Typography variant="h4">
                    {processData.performanceMetrics.activeProcesses}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Tempo Médio
                  </Typography>
                  <Typography variant="h4">
                    {processData.performanceMetrics.averageTime}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Processos Ativos */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Processos Ativos"
              avatar={<TimelineIcon />}
              action={
                <IconButton onClick={handleLogsClick}>
                  <HistoryIcon />
                </IconButton>
              }
            />
            <CardContent>
              {processData.activeProcesses.map((process) => (
                <Accordion key={process.id} sx={{ mb: 2 }}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`process-${process.id}-content`}
                    id={`process-${process.id}-header`}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6">
                          {process.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Última atualização: {process.lastUpdate}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Chip
                          label={process.status}
                          color={getStatusColor(process.status)}
                          sx={{ mr: 2 }}
                        />
                        <LinearProgress
                          variant="determinate"
                          value={process.progress}
                          sx={{ width: 100 }}
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Etapas:
                        </Typography>
                        <List>
                          {process.steps.map((step) => (
                            <ListItem
                              key={step.id}
                              button
                              onClick={() => handleStepClick(step)}
                              sx={{ mb: 1 }}
                            >
                              <ListItemIcon>
                                {getStepIcon(step.type)}
                              </ListItemIcon>
                              <ListItemText
                                primary={step.name}
                                secondary={`Tipo: ${step.type}`}
                              />
                              <Chip
                                label={step.status}
                                color={getStatusColor(step.status)}
                                size="small"
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Integrações:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          {process.integrations.map((integration) => (
                            <Chip
                              key={integration.id}
                              label={integration.name}
                              avatar={<Avatar>{integration.name[0]}</Avatar>}
                              color={integration.status === 'active' ? 'success' : 'default'}
                              size="small"
                            />
                          ))}
                        </Box>
                        <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }}>
                          Métricas:
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2">
                            Eficiência: {process.metrics.efficiency}%
                          </Typography>
                          <Typography variant="body2">
                            Precisão: {process.metrics.accuracy}%
                          </Typography>
                          <Typography variant="body2">
                            Velocidade: {process.metrics.speed}
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
                {processData.notifications.map((notification) => (
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

      {/* Diálogo de Configuração da Etapa */}
      <Dialog open={showStepConfig} onClose={handleCloseStepConfig} maxWidth="md" fullWidth>
        <DialogTitle>Configuração da Etapa</DialogTitle>
        <DialogContent>
          {selectedStep && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedStep.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Tipo: {selectedStep.type}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2">Configurações:</Typography>
              <Box component={Paper} sx={{ p: 2, mt: 1 }}>
                <Code>
                  {JSON.stringify(selectedStep.config, null, 2)}
                </Code>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseStepConfig}>Fechar</Button>
          <Button onClick={handleCloseStepConfig} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo de Logs */}
      <Dialog open={showLogs} onClose={handleCloseLogs} maxWidth="md" fullWidth>
        <DialogTitle>Logs do Processo</DialogTitle>
        <DialogContent>
          <List>
            {processData.activeProcesses[0].logs.map((log) => (
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

export default ProcessAutomationDashboard; 