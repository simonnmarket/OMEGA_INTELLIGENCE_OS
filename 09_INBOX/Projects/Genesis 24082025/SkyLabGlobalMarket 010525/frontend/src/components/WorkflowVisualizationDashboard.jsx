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
  Switch
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
  DragIndicator as DragIndicatorIcon
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

const WorkflowVisualizationDashboard = () => {
  const [workflowData, setWorkflowData] = useState({
    activeWorkflows: [
      {
        id: 1,
        name: 'Execução de Ordens',
        status: 'running',
        progress: 75,
        steps: [
          { id: 1, name: 'Análise de Mercado', status: 'completed', assignedTo: 'IA-1' },
          { id: 2, name: 'Validação de Risco', status: 'running', assignedTo: 'IA-2' },
          { id: 3, name: 'Execução', status: 'pending', assignedTo: 'EA-1' }
        ],
        participants: [
          { id: 1, name: 'IA-1', role: 'Análise', status: 'active' },
          { id: 2, name: 'IA-2', role: 'Risco', status: 'active' },
          { id: 3, name: 'EA-1', role: 'Execução', status: 'active' }
        ],
        lastUpdate: '2024-03-01 10:00',
        metrics: {
          efficiency: 85,
          accuracy: 92,
          speed: '2s'
        }
      },
      {
        id: 2,
        name: 'Reconciliação',
        status: 'completed',
        progress: 100,
        steps: [
          { id: 1, name: 'Coleta de Dados', status: 'completed', assignedTo: 'IA-3' },
          { id: 2, name: 'Comparação', status: 'completed', assignedTo: 'IA-3' },
          { id: 3, name: 'Relatório', status: 'completed', assignedTo: 'IA-3' }
        ],
        participants: [
          { id: 1, name: 'IA-3', role: 'Reconciliação', status: 'active' }
        ],
        lastUpdate: '2024-03-01 09:30',
        metrics: {
          efficiency: 95,
          accuracy: 100,
          speed: '1s'
        }
      }
    ],
    availableTemplates: [
      { id: 1, name: 'Execução de Ordens', description: 'Fluxo para execução de ordens de trading' },
      { id: 2, name: 'Reconciliação', description: 'Fluxo para reconciliação de transações' },
      { id: 3, name: 'Análise de Mercado', description: 'Fluxo para análise de mercado' }
    ],
    performanceMetrics: {
      totalWorkflows: 15,
      activeWorkflows: 8,
      completionRate: 92,
      averageTime: '2.5h'
    },
    notifications: [
      { id: 1, type: 'warning', message: 'Workflow "Execução de Ordens" está atrasado', timestamp: '2024-03-01 10:15' },
      { id: 2, type: 'info', message: 'Novo template disponível: Análise de Mercado', timestamp: '2024-03-01 09:30' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewWorkflowDialog, setShowNewWorkflowDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [draggedStep, setDraggedStep] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(true);
  };

  const handleCloseNewWorkflowDialog = () => {
    setShowNewWorkflowDialog(false);
  };

  const handleTemplateChange = (event) => {
    setSelectedTemplate(event.target.value);
  };

  const handleWorkflowNameChange = (event) => {
    setNewWorkflowName(event.target.value);
  };

  const handleDragStart = (result) => {
    setDraggedStep(result.draggableId);
  };

  const handleDragEnd = (result) => {
    setDraggedStep(null);
    if (!result.destination) return;

    const workflowId = parseInt(result.destination.droppableId);
    const workflow = workflowData.activeWorkflows.find(w => w.id === workflowId);
    const steps = Array.from(workflow.steps);
    const [reorderedStep] = steps.splice(result.source.index, 1);
    steps.splice(result.destination.index, 0, reorderedStep);

    setWorkflowData(prev => ({
      ...prev,
      activeWorkflows: prev.activeWorkflows.map(w =>
        w.id === workflowId ? { ...w, steps } : w
      )
    }));
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

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Visualização de Workflows
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
                    Taxa de Conclusão
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {workflowData.performanceMetrics.completionRate}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={workflowData.performanceMetrics.completionRate}
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
            />
            <CardContent>
              <DragDropContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
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
                            Etapas:
                          </Typography>
                          <Droppable droppableId={workflow.id.toString()}>
                            {(provided) => (
                              <List {...provided.droppableProps} ref={provided.innerRef}>
                                {workflow.steps.map((step, index) => (
                                  <Draggable key={step.id} draggableId={step.id.toString()} index={index}>
                                    {(provided) => (
                                      <ListItem
                                        ref={provided.innerRef}
                                        {...provided.draggableProps}
                                        {...provided.dragHandleProps}
                                        sx={{ mb: 1 }}
                                      >
                                        <ListItemIcon>
                                          <DragIndicatorIcon />
                                        </ListItemIcon>
                                        <ListItemText
                                          primary={step.name}
                                          secondary={`Atribuído a: ${step.assignedTo}`}
                                        />
                                        <Chip
                                          label={step.status}
                                          color={getStatusColor(step.status)}
                                          size="small"
                                        />
                                      </ListItem>
                                    )}
                                  </Draggable>
                                ))}
                                {provided.placeholder}
                              </List>
                            )}
                          </Droppable>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" color="text.secondary">
                            Participantes:
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            {workflow.participants.map((participant) => (
                              <Chip
                                key={participant.id}
                                label={participant.name}
                                avatar={<Avatar>{participant.name[0]}</Avatar>}
                                color={participant.status === 'active' ? 'success' : 'default'}
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
              </DragDropContext>
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

      {/* Diálogo de Novo Workflow */}
      <Dialog open={showNewWorkflowDialog} onClose={handleCloseNewWorkflowDialog}>
        <DialogTitle>Criar Novo Workflow</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Template</InputLabel>
            <Select
              value={selectedTemplate}
              onChange={handleTemplateChange}
              label="Template"
            >
              {workflowData.availableTemplates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Nome do Workflow"
            value={newWorkflowName}
            onChange={handleWorkflowNameChange}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseNewWorkflowDialog}>Cancelar</Button>
          <Button onClick={handleCloseNewWorkflowDialog} variant="contained">
            Criar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowVisualizationDashboard; 