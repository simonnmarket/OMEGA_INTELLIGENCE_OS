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
  useTheme,
  Typography,
} from '@mui/material';

interface RecentTradesProps {
  trades: Array<{
    id: string;
    asset: {
      symbol: string;
      name: string;
    };
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
    date: string;
  }>;
}

export const RecentTrades: React.FC<RecentTradesProps> = ({ trades }) => {
  const theme = useTheme();

  return (
    <Box>
      {trades.length === 0 ? (
        <Typography color="text.secondary" align="center">
          Nenhuma operação recente
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Ativo</TableCell>
                <TableCell align="right">Tipo</TableCell>
                <TableCell align="right">Quantidade</TableCell>
                <TableCell align="right">Preço</TableCell>
                <TableCell align="right">Data</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trades.map((trade) => (
                <TableRow key={trade.id}>
                  <TableCell component="th" scope="row">
                    {trade.asset.symbol}
                    <Typography variant="body2" color="text.secondary">
                      {trade.asset.name}
                    </Typography>
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color:
                        trade.type === 'buy'
                          ? theme.palette.success.main
                          : theme.palette.error.main,
                    }}
                  >
                    {trade.type === 'buy' ? 'Compra' : 'Venda'}
                  </TableCell>
                  <TableCell align="right">{trade.quantity}</TableCell>
                  <TableCell align="right">
                    {trade.price.toLocaleString('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    })}
                  </TableCell>
                  <TableCell align="right">
                    {new Date(trade.date).toLocaleDateString('pt-BR')}
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