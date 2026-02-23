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
  FormControlLabel
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
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
  DataObject as DataObjectIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

const AIDataAnalysisDashboard = () => {
  const [analysisData, setAnalysisData] = useState({
    insights: {
      marketTrend: 'alta',
      confidence: 85,
      keyPatterns: [
        { id: 1, pattern: 'Tendência de Alta', confidence: 92, impact: 'alto' },
        { id: 2, pattern: 'Suporte Forte', confidence: 88, impact: 'médio' },
        { id: 3, pattern: 'Volume Crescente', confidence: 75, impact: 'baixo' }
      ],
      predictions: [
        { date: '2024-03-01', value: 100, prediction: 105 },
        { date: '2024-03-02', value: 102, prediction: 108 },
        { date: '2024-03-03', value: 104, prediction: 112 }
      ]
    },
    recommendations: [
      { id: 1, type: 'Compra', asset: 'AAPL', confidence: 92, reason: 'Tendência de alta forte' },
      { id: 2, type: 'Venda', asset: 'GOOGL', confidence: 85, reason: 'Resistência próxima' },
      { id: 3, type: 'Manter', asset: 'BTC', confidence: 78, reason: 'Consolidação em curso' }
    ],
    dataSources: [
      { id: 1, name: 'MetaTrader 5', status: 'active', lastUpdate: '2024-03-01 10:00' },
      { id: 2, name: 'API Financeira', status: 'active', lastUpdate: '2024-03-01 10:00' },
      { id: 3, name: 'Dados Históricos', status: 'active', lastUpdate: '2024-03-01 09:00' }
    ],
    modelSettings: {
      sensitivity: 75,
      predictionHorizon: 7,
      autoUpdate: true
    }
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const [selectedModel, setSelectedModel] = useState('default');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSettingsDialog = () => {
    setShowSettingsDialog(true);
  };

  const handleCloseSettingsDialog = () => {
    setShowSettingsDialog(false);
  };

  const handleModelChange = (event) => {
    setSelectedModel(event.target.value);
  };

  const handleSensitivityChange = (event, newValue) => {
    setAnalysisData(prev => ({
      ...prev,
      modelSettings: {
        ...prev.modelSettings,
        sensitivity: newValue
      }
    }));
  };

  const handleAutoUpdateChange = (event) => {
    setAnalysisData(prev => ({
      ...prev,
      modelSettings: {
        ...prev.modelSettings,
        autoUpdate: event.target.checked
      }
    }));
  };

  const getImpactColor = (impact) => {
    switch (impact) {
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

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" component="h1">
              Análise de Dados com IA
            </Typography>
            <Box>
              <Tooltip title="Configurações">
                <IconButton sx={{ mr: 1 }} onClick={handleSettingsDialog}>
                  <SettingsIcon />
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

        {/* Insights */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Insights do Mercado"
              avatar={<PsychologyIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Tendência Atual
                  </Typography>
                  <Typography variant="h4" color={analysisData.insights.marketTrend === 'alta' ? 'success' : 'error'}>
                    {analysisData.insights.marketTrend.toUpperCase()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Confiança
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h4" sx={{ mr: 1 }}>
                      {analysisData.insights.confidence}%
                    </Typography>
                    <CircularProgress
                      variant="determinate"
                      value={analysisData.insights.confidence}
                      color={analysisData.insights.confidence >= 80 ? 'success' : 'warning'}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={analysisData.insights.predictions}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
                        <Area type="monotone" dataKey="prediction" stroke="#82ca9d" fill="#82ca9d" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Padrões Identificados */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Padrões Identificados"
              avatar={<AutoGraphIcon />}
            />
            <CardContent>
              <List>
                {analysisData.insights.keyPatterns.map((pattern) => (
                  <ListItem
                    key={pattern.id}
                    secondaryAction={
                      <Chip
                        label={pattern.impact}
                        color={getImpactColor(pattern.impact)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <LightbulbIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={pattern.pattern}
                      secondary={`Confiança: ${pattern.confidence}%`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recomendações */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Recomendações"
              avatar={<TrendingUpIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Ação</TableCell>
                      <TableCell>Ativo</TableCell>
                      <TableCell align="right">Confiança</TableCell>
                      <TableCell>Razão</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analysisData.recommendations.map((recommendation) => (
                      <TableRow key={recommendation.id}>
                        <TableCell>
                          <Chip
                            label={recommendation.type}
                            color={recommendation.type === 'Compra' ? 'success' : recommendation.type === 'Venda' ? 'error' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{recommendation.asset}</TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography sx={{ mr: 1 }}>{recommendation.confidence}%</Typography>
                            <LinearProgress
                              variant="determinate"
                              value={recommendation.confidence}
                              sx={{ width: 50 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>{recommendation.reason}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Fontes de Dados */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Fontes de Dados"
              avatar={<DataObjectIcon />}
            />
            <CardContent>
              <List>
                {analysisData.dataSources.map((source) => (
                  <ListItem
                    key={source.id}
                    secondaryAction={
                      <Chip
                        label={source.status}
                        color={source.status === 'active' ? 'success' : 'error'}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <DataObjectIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={source.name}
                      secondary={`Última atualização: ${source.lastUpdate}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Diálogo de Configurações */}
      <Dialog open={showSettingsDialog} onClose={handleCloseSettingsDialog}>
        <DialogTitle>Configurações do Modelo</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Modelo de Análise</InputLabel>
            <Select
              value={selectedModel}
              onChange={handleModelChange}
              label="Modelo de Análise"
            >
              <MenuItem value="default">Padrão</MenuItem>
              <MenuItem value="advanced">Avançado</MenuItem>
              <MenuItem value="custom">Personalizado</MenuItem>
            </Select>
          </FormControl>
          <Box sx={{ mt: 2 }}>
            <Typography gutterBottom>Sensibilidade do Modelo</Typography>
            <Slider
              value={analysisData.modelSettings.sensitivity}
              onChange={handleSensitivityChange}
              aria-labelledby="sensitivity-slider"
              valueLabelDisplay="auto"
              step={5}
              marks
              min={0}
              max={100}
            />
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={analysisData.modelSettings.autoUpdate}
                onChange={handleAutoUpdateChange}
              />
            }
            label="Atualização Automática"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSettingsDialog}>Cancelar</Button>
          <Button onClick={handleCloseSettingsDialog} variant="contained">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIDataAnalysisDashboard; 