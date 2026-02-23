import React from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  useTheme,
} from '@mui/material';
import { useAppSelector } from '@store/hooks';
import { selectPortfolio } from '@store/portfolio/portfolioSlice';
import { selectTrading } from '@store/trading/tradingSlice';

export const PortfolioSummary: React.FC = () => {
  const theme = useTheme();
  const { currentPortfolio } = useAppSelector(selectPortfolio);
  const { positions } = useAppSelector(selectTrading);

  const totalValue = currentPortfolio?.totalValue || 0;
  const totalInvested = positions.reduce(
    (sum, position) => sum + position.quantity * position.entryPrice,
    0
  );
  const totalProfitLoss = positions.reduce(
    (sum, position) => sum + position.profitLoss,
    0
  );
  const totalProfitLossPercentage = (totalProfitLoss / totalInvested) * 100 || 0;

  const summaryData = [
    {
      label: 'Valor Total',
      value: totalValue.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }),
    },
    {
      label: 'Valor Investido',
      value: totalInvested.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }),
    },
    {
      label: 'Lucro/Prejuízo',
      value: totalProfitLoss.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }),
      color: totalProfitLoss >= 0 ? theme.palette.success.main : theme.palette.error.main,
    },
    {
      label: 'Rentabilidade',
      value: `${totalProfitLossPercentage.toFixed(2)}%`,
      color: totalProfitLossPercentage >= 0 ? theme.palette.success.main : theme.palette.error.main,
    },
  ];

  return (
    <Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Métrica</TableCell>
              <TableCell align="right">Valor</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {summaryData.map((row) => (
              <TableRow key={row.label}>
                <TableCell component="th" scope="row">
                  {row.label}
                </TableCell>
                <TableCell
                  align="right"
                  sx={{ color: row.color || theme.palette.text.primary }}
                >
                  {row.value}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}; 