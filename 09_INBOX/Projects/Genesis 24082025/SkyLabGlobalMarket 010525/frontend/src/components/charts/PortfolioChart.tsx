import React from 'react';
import { Box, useTheme } from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useAppSelector } from '@store/hooks';
import { selectPortfolio } from '@store/portfolio/portfolioSlice';

export const PortfolioChart: React.FC = () => {
  const theme = useTheme();
  const { currentPortfolio } = useAppSelector(selectPortfolio);

  // Dados de exemplo - substituir por dados reais da API
  const data = [
    { date: '2023-01', value: 10000 },
    { date: '2023-02', value: 10500 },
    { date: '2023-03', value: 11000 },
    { date: '2023-04', value: 11500 },
    { date: '2023-05', value: 12000 },
    { date: '2023-06', value: 12500 },
    { date: '2023-07', value: 13000 },
  ];

  return (
    <Box sx={{ height: 400 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
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
          <Line
            type="monotone"
            dataKey="value"
            name="Valor do Portfólio"
            stroke={theme.palette.primary.main}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
}; 