import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { generateReport } from '../store/reportsSlice';

const Reports = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [reportType, setReportType] = useState('performance');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      await dispatch(generateReport({
        type: reportType,
        startDate,
        endDate
      }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Relatórios
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Tipo de Relatório</InputLabel>
              <Select
                value={reportType}
                label="Tipo de Relatório"
                onChange={(e) => setReportType(e.target.value)}
              >
                <MenuItem value="performance">Desempenho</MenuItem>
                <MenuItem value="risk">Risco</MenuItem>
                <MenuItem value="trades">Operações</MenuItem>
                <MenuItem value="portfolio">Portfólio</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <DatePicker
              label="Data Inicial"
              value={startDate}
              onChange={setStartDate}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <DatePicker
              label="Data Final"
              value={endDate}
              onChange={setEndDate}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </Grid>

          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerateReport}
              disabled={loading || !startDate || !endDate}
            >
              {loading ? <CircularProgress size={24} /> : 'Gerar Relatório'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Relatórios Gerados
        </Typography>
        {/* Aqui será exibido o relatório gerado */}
      </Paper>
    </Box>
  );
};

export default Reports; 