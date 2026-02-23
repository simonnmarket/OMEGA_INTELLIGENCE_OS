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
  Checkbox,
  Badge,
  LinearProgress,
  Slider,
  Switch,
  FormControlLabel,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  AvatarGroup
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Description as DescriptionIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  AutoGraph as AutoGraphIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  DataObject as DataObjectIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Share as ShareIcon,
  Notifications as NotificationsIcon,
  Api as ApiIcon,
  IntegrationInstructions as IntegrationIcon,
  SmartToy as SmartToyIcon,
  PsychologyAlt as PsychologyAltIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

const AutomationDashboard = () => {
  const [automationData, setAutomationData] = useState({
    activeAutomations: [
      {
        id: 1,
        name: 'Análise de Mercado',
        type: 'IA',
        status: 'running',
        progress: 85,
        integrations: [
          { id: 1, name: 'MetaTrader 5', status: 'active' },
          { id: 2, name: 'API Financeira', status: 'active' },
          { id: 3, name: 'Modelo de IA', status: 'active' }
        ],
        lastUpdate: '2024-03-01 10:00',
        performance: {
          accuracy: 92,
          speed: '2s',
          reliability: 98
        }
      },
      {
        id: 2,
        name: 'Execução de Ordens',
        type: 'EA',
        status: 'completed',
        progress: 100,
        integrations: [
          { id: 1, name: 'MetaTrader 5', status: 'active' },
          { id: 2, name: 'API de Execução', status: 'active' }
        ],
        lastUpdate: '2024-03-01 09:30',
        performance: {
          accuracy: 100,
          speed: '1s',
          reliability: 100
        }
      }
    ],
    availableIntegrations: [
      { id: 1, name: 'MetaTrader 5', type: 'Trading', status: 'active' },
      { id: 2, name: 'API Financeira', type: 'Dados', status: 'active' },
      { id: 3, name: 'TensorFlow', type: 'IA', status: 'active' },
      { id: 4, name: 'Hugging Face', type: 'IA', status: 'active' }
    ],
    performanceMetrics: {
      totalAutomations: 12,
      activeAutomations: 8,
      successRate: 95,
      averageResponseTime: '1.5s'
    },
    notifications: [
      { id: 1, type: 'warning', message: 'Automação "Análise de Mercado" detectou anomalia', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Nova integração disponível: Hugging Face', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewAutomationDialog, setShowNewAutomationDialog] = useState(false);
  const [selectedType, setSelectedType] = useState('');
  const [newAutomationName, setNewAutomationName] = useState('');
  const [selectedIntegrations, setSelectedIntegrations] = useState([]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewAutomationDialog = () => {
    setShowNewAutomationDialog(true);
  };

  const handleCloseNewAutomationDialog = () => {
    setShowNewAutomationDialog(false);
  };

  const handleTypeChange = (event) => {
    setSelectedType(event.target.value);
  };

  const handleAutomationNameChange = (event) => {
    setNewAutomationName(event.target.value);
  };

  const handleIntegrationToggle = (integrationId) => {
    setSelectedIntegrations(prev => {
      if (prev.includes(integrationId)) {
        return prev.filter(id => id !== integrationId);
      } else {
        return [...prev, integrationId];
      }
    });
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

  const getTypeIcon = (type) => {
    switch (type) {
      case 'IA':
        return <PsychologyAltIcon />;
      case 'EA':
        return <SmartToyIcon />;
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
              Automação e IA
            </Typography>
            <Box>
              <Tooltip title="Nova Automação">
                <IconButton sx={{ mr: 1 }} onClick={handleNewAutomationDialog}>
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
              avatar={<BarChartIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Total de Automações
                  </Typography>
                  <Typography variant="h4">
                    {automationData.performanceMetrics.totalAutomations}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Taxa de Sucesso
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {automationData.performanceMetrics.successRate}%
                    </Typography>
                    <CircularProgress
                      variant="determinate"
                      value={automationData.performanceMetrics.successRate}
                      color="success"
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Automações Ativas
                  </Typography>
                  <Typography variant="h4">
                    {automationData.performanceMetrics.activeAutomations}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h6" color="text.secondary">
                    Tempo Médio de Resposta
                  </Typography>
                  <Typography variant="h4">
                    {automationData.performanceMetrics.averageResponseTime}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Automações Ativas */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Automações Ativas"
              avatar={<AutoAwesomeIcon />}
            />
            <CardContent>
              {automationData.activeAutomations.map((automation) => (
                <Accordion key={automation.id} sx={{ mb: 2 }}>
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon />}
                    aria-controls={`automation-${automation.id}-content`}
                    id={`automation-${automation.id}-header`}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getTypeIcon(automation.type)}
                          <Typography variant="h6" sx={{ ml: 1 }}>
                            {automation.name}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Última atualização: {automation.lastUpdate}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Chip
                          label={automation.status}
                          color={getStatusColor(automation.status)}
                          sx={{ mr: 2 }}
                        />
                        <LinearProgress
                          variant="determinate"
                          value={automation.progress}
                          sx={{ width: 100 }}
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Integrações:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          {automation.integrations.map((integration) => (
                            <Chip
                              key={integration.id}
                              label={integration.name}
                              color={integration.status === 'active' ? 'success' : 'default'}
                              size="small"
                            />
                          ))}
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Performance:
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2">
                            Precisão: {automation.performance.accuracy}%
                          </Typography>
                          <Typography variant="body2">
                            Velocidade: {automation.performance.speed}
                          </Typography>
                          <Typography variant="body2">
                            Confiabilidade: {automation.performance.reliability}%
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
                {automationData.notifications.map((notification) => (
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

      {/* Diálogo de Nova Automação */}
      <Dialog open={showNewAutomationDialog} onClose={handleCloseNewAutomationDialog}>
        <DialogTitle>Criar Nova Automação</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Tipo de Automação</InputLabel>
            <Select
              value={selectedType}
              onChange={handleTypeChange}
              label="Tipo de Automação"
            >
              <MenuItem value="IA">Inteligência Artificial</MenuItem>
              <MenuItem value="EA">Expert Advisor</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Nome da Automação"
            value={newAutomationName}
            onChange={handleAutomationNameChange}
            sx={{ mt: 2 }}
          />
          <Typography variant="subtitle2" sx={{ mt: 2 }}>
            Integrações Disponíveis:
          </Typography>
          <List>
            {automationData.availableIntegrations.map((integration) => (
              <ListItem key={integration.id}>
                <ListItemIcon>
                  <IntegrationIcon />
                </ListItemIcon>
                <ListItemText primary={integration.name} secondary={integration.type} />
                <Checkbox
                  edge="end"
                  checked={selectedIntegrations.includes(integration.id)}
                  onChange={() => handleIntegrationToggle(integration.id)}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseNewAutomationDialog}>Cancelar</Button>
          <Button onClick={handleCloseNewAutomationDialog} variant="contained">
            Criar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationDashboard; 