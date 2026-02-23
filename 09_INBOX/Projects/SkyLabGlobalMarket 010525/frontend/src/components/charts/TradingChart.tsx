import React from 'react';
import { Box, useTheme } from '@mui/material';
import {
  CandlestickChart,
  Candlestick,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useAppSelector } from '@store/hooks';
import { selectTrading } from '@store/trading/tradingSlice';

export const TradingChart: React.FC = () => {
  const theme = useTheme();
  const { selectedAsset } = useAppSelector(selectTrading);

  // Dados de exemplo - substituir por dados reais da API
  const data = [
    {
      date: '2023-01-01',
      open: 100,
      high: 105,
      low: 95,
      close: 102,
    },
    {
      date: '2023-01-02',
      open: 102,
      high: 108,
      low: 100,
      close: 106,
    },
    {
      date: '2023-01-03',
      open: 106,
      high: 110,
      low: 104,
      close: 108,
    },
    {
      date: '2023-01-04',
      open: 108,
      high: 112,
      low: 106,
      close: 110,
    },
    {
      date: '2023-01-05',
      open: 110,
      high: 115,
      low: 108,
      close: 112,
    },
  ];

  return (
    <Box sx={{ height: 400 }}>
      <ResponsiveContainer width="100%" height="100%">
        <CandlestickChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fill: theme.palette.text.primary }}
            axisLine={{ stroke: theme.palette.divider }}
          />
          <YAxis
            tick={{ fill: theme.palette.text.primary }}
            axisLine={{ stroke: theme.palette.divider }}
            tickFormatter={(value) =>
              value.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              })
            }
          />
          <Tooltip
            formatter={(value: number) =>
              value.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              })
            }
            labelStyle={{ color: theme.palette.text.primary }}
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              borderColor: theme.palette.divider,
            }}
          />
          <Legend />
          <Candlestick
            dataKey="open"
            dataKey2="close"
            dataKey3="high"
            dataKey4="low"
            name={selectedAsset?.symbol || 'Ativo'}
            fill={theme.palette.primary.main}
            stroke={theme.palette.primary.main}
          />
        </CandlestickChart>
      </ResponsiveContainer>
    </Box>
  );
}; 