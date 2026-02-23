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
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const WorkflowAutomationDashboard = () => {
  const [workflowData, setWorkflowData] = useState({
    activeWorkflows: [
      {
        id: 1,
        name: 'Análise e Execução',
        status: 'running',
        progress: 75,
        nodes: [
          { id: 1, type: 'IA', name: 'Análise de Mercado', status: 'completed', config: { model: 'TensorFlow', version: '2.0' } },
          { id: 2, type: 'IA', name: 'Validação de Risco', status: 'running', config: { model: 'HuggingFace', version: '1.0' } },
          { id: 3, type: 'EA', name: 'Execução de Ordens', status: 'pending', config: { platform: 'MetaTrader 5' } }
        ],
        connections: [
          { from: 1, to: 2 },
          { from: 2, to: 3 }
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
          { id: 1, timestamp: '2024-03-01 10:00', level: 'info', message: 'Workflow iniciado' },
          { id: 2, timestamp: '2024-03-01 10:01', level: 'success', message: 'Análise de Mercado concluída' },
          { id: 3, timestamp: '2024-03-01 10:02', level: 'warning', message: 'Validação de Risco em andamento' }
        ]
      }
    ],
    availableNodes: [
      { id: 1, type: 'IA', name: 'Análise de Mercado', description: 'Modelo de IA para análise de mercado' },
      { id: 2, type: 'IA', name: 'Validação de Risco', description: 'Modelo de IA para validação de risco' },
      { id: 3, type: 'EA', name: 'Execução de Ordens', description: 'EA para execução de ordens' },
      { id: 4, type: 'API', name: 'Coleta de Dados', description: 'Integração com API financeira' }
    ],
    performanceMetrics: {
      totalWorkflows: 15,
      activeWorkflows: 8,
      successRate: 92,
      averageTime: '2.5h'
    },
    notifications: [
      { id: 1, type: 'warning', message: 'Workflow "Análise e Execução" está atrasado', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Nova integração disponível: Alpha Vantage', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewWorkflowDialog, setShowNewWorkflowDialog] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showNodeConfig, setShowNodeConfig] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(true);
  };

  const handleCloseNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(false);
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    setShowNodeConfig(true);
  };

  const handleCloseNodeConfig = () => {
    setShowNodeConfig(false);
    setSelectedNode(null);
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

  const getNodeIcon = (type) => {
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
              Automação de Workflows
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
                    Total de Workflows
                  </Typography>
                  <Typography variant="h4">
                    {workflowData.performanceMetrics.totalWorkflows}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Sucesso
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {workflowData.performanceMetrics.successRate}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={workflowData.performanceMetrics.successRate}
                      sx={{ width: 100 }}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Workflows Ativos
                  </Typography>
                  <Typography variant="h4">
                    {workflowData.performanceMetrics.activeWorkflows}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Tempo Médio
                  </Typography>
                  <Typography variant="h4">
                    {workflowData.performanceMetrics.averageTime}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflows Ativos */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Workflows Ativos"
              avatar={<TimelineIcon />}
              action={
                <IconButton onClick={handleLogsClick}>
                  <HistoryIcon />
                </IconButton>
              }
            />
            <CardContent>
              {workflowData.activeWorkflows.map((workflow) => (
                <Accordion key={workflow.id} sx={{ mb: 2 }}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`workflow-${workflow.id}-content`}
                    id={`workflow-${workflow.id}-header`}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6">
                          {workflow.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Última atualização: {workflow.lastUpdate}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Chip
                          label={workflow.status}
                          color={getStatusColor(workflow.status)}
                          sx={{ mr: 2 }}
                        />
                        <LinearProgress
                          variant="determinate"
                          value={workflow.progress}
                          sx={{ width: 100 }}
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Nós:
                        </Typography>
                        <List>
                          {workflow.nodes.map((node) => (
                            <ListItem
                              key={node.id}
                              button
                              onClick={() => handleNodeClick(node)}
                              sx={{ mb: 1 }}
                            >
                              <ListItemIcon>
                                {getNodeIcon(node.type)}
                              </ListItemIcon>
                              <ListItemText
                                primary={node.name}
                                secondary={`Tipo: ${node.type}`}
                              />
                              <Chip
                                label={node.status}
                                color={getStatusColor(node.status)}
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
                          {workflow.integrations.map((integration) => (
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
                            Eficiência: {workflow.metrics.efficiency}%
                          </Typography>
                          <Typography variant="body2">
                            Precisão: {workflow.metrics.accuracy}%
                          </Typography>
                          <Typography variant="body2">
                            Velocidade: {workflow.metrics.speed}
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

      {/* Diálogo de Configuração do Nó */}
      <Dialog open={showNodeConfig} onClose={handleCloseNodeConfig} maxWidth="md" fullWidth>
        <DialogTitle>Configuração do Nó</DialogTitle>
        <DialogContent>
          {selectedNode && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">{selectedNode.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Tipo: {selectedNode.type}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2">Configurações:</Typography>
              <Box component={Paper} sx={{ p: 2, mt: 1 }}>
                <Code>
                  {JSON.stringify(selectedNode.config, null, 2)}
                </Code>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseNodeConfig}>Fechar</Button>
          <Button onClick={handleCloseNodeConfig} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Diálogo de Logs */}
      <Dialog open={showLogs} onClose={handleCloseLogs} maxWidth="md" fullWidth>
        <DialogTitle>Logs do Workflow</DialogTitle>
        <DialogContent>
          <List>
            {workflowData.activeWorkflows[0].logs.map((log) => (
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

export default WorkflowAutomationDashboard; 