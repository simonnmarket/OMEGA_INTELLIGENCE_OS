import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress
} from '@mui/material';
import { fetchPortfolioData, addAsset } from '../store/portfolioSlice';

const PortfolioManagement = () => {
  const dispatch = useDispatch();
  const { data: portfolio, loading } = useSelector(state => state.portfolio);
  const [openDialog, setOpenDialog] = useState(false);
  const [newAsset, setNewAsset] = useState({
    symbol: '',
    allocation: '',
    targetPrice: ''
  });

  useEffect(() => {
    dispatch(fetchPortfolioData());
  }, [dispatch]);

  const handleAddAsset = () => {
    dispatch(addAsset(newAsset));
    setOpenDialog(false);
    setNewAsset({ symbol: '', allocation: '', targetPrice: '' });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Gestão de Portfólio</Typography>
        <Button variant="contained" color="primary" onClick={() => setOpenDialog(true)}>
          Adicionar Ativo
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Ativo</TableCell>
              <TableCell>Alocação (%)</TableCell>
              <TableCell>Preço Atual</TableCell>
              <TableCell>Preço Alvo</TableCell>
              <TableCell>Retorno (%)</TableCell>
              <TableCell>Volume Operado</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {portfolio.map((item, index) => (
              <TableRow key={index}>
                <TableCell>{item.symbol}</TableCell>
                <TableCell>{item.allocation}</TableCell>
                <TableCell>{item.currentPrice}</TableCell>
                <TableCell>{item.targetPrice}</TableCell>
                <TableCell color={item.return >= 0 ? "success" : "error"}>
                  {item.return}%
                </TableCell>
                <TableCell>{item.volume}</TableCell>
                <TableCell>
                  <Button size="small" color="primary">Editar</Button>
                  <Button size="small" color="error">Remover</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Adicionar Novo Ativo</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Símbolo"
            fullWidth
            value={newAsset.symbol}
            onChange={(e) => setNewAsset({ ...newAsset, symbol: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Alocação (%)"
            type="number"
            fullWidth
            value={newAsset.allocation}
            onChange={(e) => setNewAsset({ ...newAsset, allocation: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Preço Alvo"
            type="number"
            fullWidth
            value={newAsset.targetPrice}
            onChange={(e) => setNewAsset({ ...newAsset, targetPrice: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button onClick={handleAddAsset} color="primary">Adicionar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortfolioManagement; 