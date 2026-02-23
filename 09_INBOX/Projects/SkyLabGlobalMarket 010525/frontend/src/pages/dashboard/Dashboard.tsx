import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
  AttachMoney as AttachMoneyIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@store/hooks';
import { selectPortfolio } from '@store/portfolio/portfolioSlice';
import { selectTrading } from '@store/trading/tradingSlice';
import { PortfolioChart } from '@components/charts/PortfolioChart';
import { RecentTrades } from '@components/trading/RecentTrades';
import { PortfolioSummary } from '@components/portfolio/PortfolioSummary';

export const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { currentPortfolio } = useAppSelector(selectPortfolio);
  const { positions } = useAppSelector(selectTrading);

  const totalProfitLoss = positions.reduce(
    (sum, position) => sum + position.profitLoss,
    0
  );

  const totalProfitLossPercentage = positions.reduce(
    (sum, position) => sum + position.profitLossPercentage,
    0
  ) / positions.length || 0;

  const stats = [
    {
      title: 'Valor Total',
      value: currentPortfolio?.totalValue.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }) || 'R$ 0,00',
      icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />,
      color: theme.palette.primary.main,
    },
    {
      title: 'Lucro/Prejuízo',
      value: totalProfitLoss.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }),
      icon: <AttachMoneyIcon sx={{ fontSize: 40 }} />,
      color: totalProfitLoss >= 0 ? theme.palette.success.main : theme.palette.error.main,
    },
    {
      title: 'Rentabilidade',
      value: `${totalProfitLossPercentage.toFixed(2)}%`,
      icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
      color: totalProfitLossPercentage >= 0 ? theme.palette.success.main : theme.palette.error.main,
    },
    {
      title: 'Posições Abertas',
      value: positions.length.toString(),
      icon: <TrendingDownIcon sx={{ fontSize: 40 }} />,
      color: theme.palette.info.main,
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h5" component="div">
                      {stat.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: stat.color }}>{stat.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Evolução do Portfólio
              </Typography>
              <PortfolioChart />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Operações Recentes
              </Typography>
              <RecentTrades />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resumo do Portfólio
              </Typography>
              <PortfolioSummary />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 