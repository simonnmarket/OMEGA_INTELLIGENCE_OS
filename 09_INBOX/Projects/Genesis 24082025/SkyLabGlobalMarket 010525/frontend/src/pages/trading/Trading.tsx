import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  useTheme,
} from '@mui/material';
import { useAppSelector } from '@store/hooks';
import { selectTrading } from '@store/trading/tradingSlice';
import { TradingForm } from '@components/trading/TradingForm';
import { PositionsList } from '@components/trading/PositionsList';
import { RecentTrades } from '@components/trading/RecentTrades';
import { TradingChart } from '@components/charts/TradingChart';

export const Trading: React.FC = () => {
  const theme = useTheme();
  const { positions, recentTrades } = useAppSelector(selectTrading);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Trading
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Gráfico de Preços
              </Typography>
              <TradingChart />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Nova Operação
              </Typography>
              <TradingForm />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Posições Abertas
              </Typography>
              <PositionsList positions={positions} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Operações Recentes
              </Typography>
              <RecentTrades trades={recentTrades} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 