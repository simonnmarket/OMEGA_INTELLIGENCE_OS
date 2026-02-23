import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  useTheme,
  Typography,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useAppDispatch } from '@store/hooks';
import { closePosition } from '@store/trading/tradingSlice';

interface PositionsListProps {
  positions: Array<{
    id: string;
    asset: {
      symbol: string;
      name: string;
    };
    type: 'buy' | 'sell';
    quantity: number;
    entryPrice: number;
    currentPrice: number;
    profitLoss: number;
    profitLossPercentage: number;
  }>;
}

export const PositionsList: React.FC<PositionsListProps> = ({ positions }) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();

  const handleClosePosition = async (positionId: string) => {
    try {
      await dispatch(closePosition(positionId)).unwrap();
    } catch (error) {
      console.error('Erro ao fechar posição:', error);
    }
  };

  return (
    <Box>
      {positions.length === 0 ? (
        <Typography color="text.secondary" align="center">
          Nenhuma posição aberta
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Ativo</TableCell>
                <TableCell align="right">Tipo</TableCell>
                <TableCell align="right">Quantidade</TableCell>
                <TableCell align="right">Preço de Entrada</TableCell>
                <TableCell align="right">Preço Atual</TableCell>
                <TableCell align="right">Lucro/Prejuízo</TableCell>
                <TableCell align="right">Rentabilidade</TableCell>
                <TableCell align="right">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((position) => (
                <TableRow key={position.id}>
                  <TableCell component="th" scope="row">
                    {position.asset.symbol}
                    <Typography variant="body2" color="text.secondary">
                      {position.asset.name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {position.type === 'buy' ? 'Compra' : 'Venda'}
                  </TableCell>
                  <TableCell align="right">{position.quantity}</TableCell>
                  <TableCell align="right">
                    {position.entryPrice.toLocaleString('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    })}
                  </TableCell>
                  <TableCell align="right">
                    {position.currentPrice.toLocaleString('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    })}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color:
                        position.profitLoss >= 0
                          ? theme.palette.success.main
                          : theme.palette.error.main,
                    }}
                  >
                    {position.profitLoss.toLocaleString('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    })}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color:
                        position.profitLossPercentage >= 0
                          ? theme.palette.success.main
                          : theme.palette.error.main,
                    }}
                  >
                    {position.profitLossPercentage.toFixed(2)}%
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleClosePosition(position.id)}
                    >
                      <CloseIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}; 