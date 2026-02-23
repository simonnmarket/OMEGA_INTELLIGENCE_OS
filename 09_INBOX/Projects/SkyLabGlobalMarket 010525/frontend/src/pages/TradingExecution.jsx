import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { executeTrade, fetchMarketData } from '../store/tradingSlice';

const TradingExecution = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState({
    symbol: '',
    type: 'buy',
    quantity: '',
    price: '',
    stopLoss: '',
    takeProfit: ''
  });
  const [marketData, setMarketData] = useState([]);

  useEffect(() => {
    const loadMarketData = async () => {
      const data = await dispatch(fetchMarketData());
      setMarketData(data);
    };
    loadMarketData();
  }, [dispatch]);

  const handleExecute = async () => {
    setLoading(true);
    try {
      await dispatch(executeTrade(order));
      setOrder({
        symbol: '',
        type: 'buy',
        quantity: '',
        price: '',
        stopLoss: '',
        takeProfit: ''
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Execução de Operações
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Nova Ordem
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Ativo</InputLabel>
                  <Select
                    value={order.symbol}
                    label="Ativo"
                    onChange={(e) => setOrder({ ...order, symbol: e.target.value })}
                  >
                    {marketData.map((asset) => (
                      <MenuItem key={asset.symbol} value={asset.symbol}>
                        {asset.symbol} - {asset.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Tipo</InputLabel>
                  <Select
                    value={order.type}
                    label="Tipo"
                    onChange={(e) => setOrder({ ...order, type: e.target.value })}
                  >
                    <MenuItem value="buy">Compra</MenuItem>
                    <MenuItem value="sell">Venda</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Quantidade"
                  type="number"
                  value={order.quantity}
                  onChange={(e) => setOrder({ ...order, quantity: e.target.value })}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Preço"
                  type="number"
                  value={order.price}
                  onChange={(e) => setOrder({ ...order, price: e.target.value })}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Stop Loss"
                  type="number"
                  value={order.stopLoss}
                  onChange={(e) => setOrder({ ...order, stopLoss: e.target.value })}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Take Profit"
                  type="number"
                  value={order.takeProfit}
                  onChange={(e) => setOrder({ ...order, takeProfit: e.target.value })}
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleExecute}
                  disabled={loading || !order.symbol || !order.quantity || !order.price}
                  fullWidth
                >
                  {loading ? <CircularProgress size={24} /> : 'Executar Ordem'}
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Dados de Mercado
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Ativo</TableCell>
                    <TableCell>Último Preço</TableCell>
                    <TableCell>Variação</TableCell>
                    <TableCell>Volume</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {marketData.map((asset) => (
                    <TableRow key={asset.symbol}>
                      <TableCell>{asset.symbol}</TableCell>
                      <TableCell>{asset.lastPrice}</TableCell>
                      <TableCell color={asset.change >= 0 ? "success" : "error"}>
                        {asset.change}%
                      </TableCell>
                      <TableCell>{asset.volume}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingExecution; 