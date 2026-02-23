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
  Badge
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  Sync as SyncIcon,
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
  Book as BookIcon,
  CompareArrows as CompareArrowsIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const InvestmentAccountingDashboard = () => {
  const [accountingData, setAccountingData] = useState({
    portfolio: {
      totalValue: 5000000,
      dailyChange: 25000,
      monthlyChange: 150000,
      positions: [
        { asset: 'Ações', value: 2000000, percentage: 40 },
        { asset: 'Títulos', value: 1500000, percentage: 30 },
        { asset: 'Commodities', value: 1000000, percentage: 20 },
        { asset: 'Moedas', value: 500000, percentage: 10 }
      ]
    },
    transactions: [
      { id: 1, type: 'Compra', asset: 'AAPL', quantity: 100, price: 150, date: '2024-03-01', status: 'completed' },
      { id: 2, type: 'Venda', asset: 'GOOGL', quantity: 50, price: 2800, date: '2024-03-01', status: 'pending' },
      { id: 3, type: 'Compra', asset: 'BTC', quantity: 1, price: 50000, date: '2024-03-01', status: 'completed' }
    ],
    reconciliation: {
      status: 'in_progress',
      lastRun: '2024-03-01 10:00',
      discrepancies: 2,
      details: [
        { id: 1, source: 'MetaTrader 5', type: 'Trade', amount: 1000, status: 'resolved' },
        { id: 2, source: 'Banco', type: 'Transferência', amount: 500, status: 'pending' }
      ]
    },
    books: [
      { id: 1, name: 'Principal', status: 'active', lastUpdate: '2024-03-01 10:00' },
      { id: 2, name: 'Reserva', status: 'active', lastUpdate: '2024-03-01 10:00' },
      { id: 3, name: 'Teste', status: 'inactive', lastUpdate: '2024-03-01 09:00' }
    ]
  });

  const [activeTab, setActiveTab] = useState(0);
  const [showNewBookDialog, setShowNewBookDialog] = useState(false);
  const [newBookName, setNewBookName] = useState('');
  const [selectedBook, setSelectedBook] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleNewBookDialog = () => {
    setShowNewBookDialog(true);
  };

  const handleCloseNewBookDialog = () => {
    setShowNewBookDialog(false);
    setNewBookName('');
  };

  const handleCreateBook = () => {
    // TODO: Implementar criação de novo livro
    handleCloseNewBookDialog();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
      case 'active':
      case 'resolved':
        return 'success';
      case 'pending':
      case 'in_progress':
        return 'warning';
      case 'error':
      case 'inactive':
        return 'error';
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
              Contabilidade de Investimentos
            </Typography>
            <Box>
              <Tooltip title="Configurações">
                <IconButton sx={{ mr: 1 }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Sincronizar">
                <IconButton>
                  <SyncIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Grid>

        {/* Portfólio */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Portfólio"
              avatar={<AccountBalanceIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Valor Total
                  </Typography>
                  <Typography variant="h4">
                    ${accountingData.portfolio.totalValue.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Variação Diária
                  </Typography>
                  <Typography variant="h4" color={accountingData.portfolio.dailyChange >= 0 ? 'success' : 'error'}>
                    ${accountingData.portfolio.dailyChange.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" color="text.secondary">
                    Variação Mensal
                  </Typography>
                  <Typography variant="h4" color={accountingData.portfolio.monthlyChange >= 0 ? 'success' : 'error'}>
                    ${accountingData.portfolio.monthlyChange.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={accountingData.portfolio.positions}
                          dataKey="value"
                          nameKey="asset"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          label
                        >
                          {accountingData.portfolio.positions.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Livros Financeiros */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Livros Financeiros"
              avatar={<BookIcon />}
              action={
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleNewBookDialog}
                >
                  Novo Livro
                </Button>
              }
            />
            <CardContent>
              <List>
                {accountingData.books.map((book) => (
                  <ListItem
                    key={book.id}
                    secondaryAction={
                      <Chip
                        label={book.status}
                        color={getStatusColor(book.status)}
                        size="small"
                      />
                    }
                  >
                    <ListItemIcon>
                      <BookIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={book.name}
                      secondary={`Última atualização: ${book.lastUpdate}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Transações */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Transações Recentes"
              avatar={<TimelineIcon />}
            />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Ativo</TableCell>
                      <TableCell align="right">Quantidade</TableCell>
                      <TableCell align="right">Preço</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {accountingData.transactions.map((transaction) => (
                      <TableRow key={transaction.id}>
                        <TableCell>{transaction.type}</TableCell>
                        <TableCell>{transaction.asset}</TableCell>
                        <TableCell align="right">{transaction.quantity}</TableCell>
                        <TableCell align="right">${transaction.price.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={transaction.status}
                            color={getStatusColor(transaction.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Reconciliação */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Reconciliação"
              avatar={<CompareArrowsIcon />}
              action={
                <Button
                  variant="outlined"
                  startIcon={<SyncIcon />}
                  onClick={() => {/* TODO: Implementar reconciliação */}}
                >
                  Executar
                </Button>
              }
            />
            <CardContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Status: {accountingData.reconciliation.status}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Última execução: {accountingData.reconciliation.lastRun}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Discrepâncias encontradas: {accountingData.reconciliation.discrepancies}
                </Typography>
              </Box>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Fonte</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell align="right">Valor</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {accountingData.reconciliation.details.map((detail) => (
                      <TableRow key={detail.id}>
                        <TableCell>{detail.source}</TableCell>
                        <TableCell>{detail.type}</TableCell>
                        <TableCell align="right">${detail.amount.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={detail.status}
                            color={getStatusColor(detail.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Diálogo de Novo Livro */}
      <Dialog open={showNewBookDialog} onClose={handleCloseNewBookDialog}>
        <DialogTitle>Criar Novo Livro Financeiro</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nome do Livro"
            fullWidth
            value={newBookName}
            onChange={(e) => setNewBookName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseNewBookDialog}>Cancelar</Button>
          <Button onClick={handleCreateBook} variant="contained">
            Criar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InvestmentAccountingDashboard; 