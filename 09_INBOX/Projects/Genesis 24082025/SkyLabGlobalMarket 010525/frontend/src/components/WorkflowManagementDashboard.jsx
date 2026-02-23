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

const WorkflowManagementDashboard = () => {
  const [workflowData, setWorkflowData] = useState({
    activeWorkflows: [
      {
        id: 1,
        name: 'Execução de Ordens',
        status: 'running',
        progress: 75,
        steps: [
          { id: 1, name: 'Análise de Mercado', status: 'completed', agent: 'IA-1' },
          { id: 2, name: 'Validação de Risco', status: 'completed', agent: 'IA-2' },
          { id: 3, name: 'Execução MT5', status: 'in-progress', agent: 'EA-1' },
          { id: 4, name: 'Confirmação', status: 'pending', agent: 'IA-3' }
        ],
        startTime: '2024-03-01 09:00',
        estimatedEnd: '2024-03-01 10:00'
      },
      {
        id: 2,
        name: 'Reconciliação Financeira',
        status: 'pending',
        progress: 0,
        steps: [
          { id: 1, name: 'Coleta de Dados', status: 'pending', agent: 'IA-4' },
          { id: 2, name: 'Análise de Discrepâncias', status: 'pending', agent: 'IA-5' },
          { id: 3, name: 'Ajustes Automáticos', status: 'pending', agent: 'EA-2' }
        ],
        startTime: '2024-03-01 10:00',
        estimatedEnd: '2024-03-01 11:00'
      }
    ],
    kpis: {
      workflowsCompleted: 150,
      averageCompletionTime: '45min',
      successRate: 95,
      automationRate: 85
    },
    notifications: [
      { id: 1, type: 'info', message: 'Novo workflow iniciado: Execução de Ordens', timestamp: '2024-03-01 09:00' },
      { id: 2, type: 'warning', message: 'Atraso na etapa de Validação de Risco', timestamp: '2024-03-01 09:30' }
    ],
    teamMembers: [
      { id: 1, name: 'IA-1', role: 'Análise de Mercado', status: 'active' },
      { id: 2, name: 'IA-2', role: 'Validação de Risco', status: 'active' },
      { id: 3, name: 'EA-1', role: 'Execução MT5', status: 'active' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewWorkflowDialog, setShowNewWorkflowDialog] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [showWorkflowDetails, setShowWorkflowDetails] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(true);
  };

  const handleCloseNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(false);
  };

  const handleWorkflowClick = (workflow) => {
    setSelectedWorkflow(workflow);
    setShowWorkflowDetails(true);
  };

  const handleCloseWorkflowDetails = () => {
    setShowWorkflowDetails(false);
    setSelectedWorkflow(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'pending':
        return 'warning';
      case 'completed':
        return 'info';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStepStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in-progress':
        return 'warning';
      case 'pending':
        return 'default';
      case 'error':
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
              Gestão de Workflows
            </Typography>
            <Box>
              <Tooltip title="Novo Workflow">
                <IconButton sx={{ mr: 1 }} onClick={handleNewWorkflowDialog}>
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

        {/* KPIs */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Indicadores de Desempenho"
              avatar={<AssessmentIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Workflows Concluídos
                  </Typography>
                  <Typography variant="h4">
                    {workflowData.kpis.workflowsCompleted}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Tempo Médio
                  </Typography>
                  <Typography variant="h4">
                    {workflowData.kpis.averageCompletionTime}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Sucesso
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {workflowData.kpis.successRate}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Automação
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {workflowData.kpis.automationRate}%
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflows Ativos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Workflows Ativos"
              avatar={<TimelineIcon />}
            />
            <CardContent>
              <List>
                {workflowData.activeWorkflows.map((workflow) => (
                  <ListItem
                    key={workflow.id}
                    button
                    onClick={() => handleWorkflowClick(workflow)}
                    secondaryAction={
                      <Chip
                        label={workflow.status}
                        color={getStatusColor(workflow.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <TimelineIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={workflow.name}
                      secondary={`Progresso: ${workflow.progress}%`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Equipe */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Equipe"
              avatar={<GroupIcon />}
            />
            <CardContent>
              <List>
                {workflowData.teamMembers.map((member) => (
                  <ListItem
                    key={member.id}
                    secondaryAction={
                      <Chip
                        label={member.status}
                        color={member.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <SmartToyIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={member.name}
                      secondary={member.role}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Notificações */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Notificações"
              avatar={<NotificationsIcon />}
            />
            <CardContent>
              <List>
                {workflowData.notifications.map((notification) => (
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

      {/* Diálogo de Detalhes do Workflow */}
      <Dialog open={showWorkflowDetails} onClose={handleCloseWorkflowDetails} maxWidth="md" fullWidth>
        <DialogTitle>Detalhes do Workflow</DialogTitle>
        <DialogContent>
          {selectedWorkflow && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedWorkflow.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {selectedWorkflow.status}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Progresso</Typography>
                <LinearProgress variant="determinate" value={selectedWorkflow.progress} />
              </Box>
              <List>
                {selectedWorkflow.steps.map((step) => (
                  <ListItem
                    key={step.id}
                    secondaryAction={
                      <Chip
                        label={step.status}
                        color={getStepStatusColor(step.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <SmartToyIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={step.name}
                      secondary={`Agente: ${step.agent}`}
                    />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Início</Typography>
                  <Typography>{selectedWorkflow.startTime}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Previsão de Término</Typography>
                  <Typography>{selectedWorkflow.estimatedEnd}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseWorkflowDetails}>Fechar</Button>
          <Button onClick={handleCloseWorkflowDetails} variant="contained" color="error">
            Cancelar Workflow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowManagementDashboard; 