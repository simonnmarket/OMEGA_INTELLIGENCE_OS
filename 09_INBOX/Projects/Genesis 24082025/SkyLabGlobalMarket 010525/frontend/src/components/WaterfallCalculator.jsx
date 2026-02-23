import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Alert
} from '@mui/material';
import {
  Calculate as CalculateIcon,
  Save as SaveIcon,
  Print as PrintIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const WaterfallCalculator = () => {
  const [inputData, setInputData] = useState({
    totalReturn: 100000,
    managementFee: 2,
    carriedInterest: 20,
    hurdleRate: 8,
    preferredReturn: 6
  });

  const [results, setResults] = useState({
    managementFeeAmount: 2000,
    carriedInterestAmount: 8000,
    preferredReturnAmount: 6000,
    netReturn: 90000,
    waterfall: [
      { name: 'Retorno Total', value: 100000 },
      { name: 'Taxa de Gestão', value: 2000 },
      { name: 'Retorno Preferencial', value: 6000 },
      { name: 'Carried Interest', value: 8000 },
      { name: 'Retorno Líquido', value: 90000 }
    ]
  });

  const handleInputChange = (field) => (event) => {
    const value = parseFloat(event.target.value);
    setInputData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateWaterfall = () => {
    const managementFeeAmount = (inputData.totalReturn * inputData.managementFee) / 100;
    const preferredReturnAmount = (inputData.totalReturn * inputData.preferredReturn) / 100;
    const carriedInterestAmount = ((inputData.totalReturn - managementFeeAmount - preferredReturnAmount) * inputData.carriedInterest) / 100;
    const netReturn = inputData.totalReturn - managementFeeAmount - preferredReturnAmount - carriedInterestAmount;

    const newWaterfall = [
      { name: 'Retorno Total', value: inputData.totalReturn },
      { name: 'Taxa de Gestão', value: managementFeeAmount },
      { name: 'Retorno Preferencial', value: preferredReturnAmount },
      { name: 'Carried Interest', value: carriedInterestAmount },
      { name: 'Retorno Líquido', value: netReturn }
    ];

    setResults({
      managementFeeAmount,
      carriedInterestAmount,
      preferredReturnAmount,
      netReturn,
      waterfall: newWaterfall
    });
  };

  const handleSave = () => {
    // TODO: Implementar salvamento dos cálculos
    console.log('Salvando cálculos:', results);
  };

  const handlePrint = () => {
    // TODO: Implementar impressão do relatório
    window.print();
  };

  const handleShare = () => {
    // TODO: Implementar compartilhamento do relatório
    console.log('Compartilhando relatório:', results);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Cabeçalho */}
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" gutterBottom>
            Cálculo de Distribuição de Lucros
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            Este módulo automatiza o cálculo de distribuição de lucros (waterfall) conforme as regras definidas.
          </Alert>
        </Grid>

        {/* Entrada de Dados */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Parâmetros de Cálculo"
              avatar={<CalculateIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Retorno Total ($)"
                    type="number"
                    value={inputData.totalReturn}
                    onChange={handleInputChange('totalReturn')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Taxa de Gestão (%)"
                    type="number"
                    value={inputData.managementFee}
                    onChange={handleInputChange('managementFee')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Carried Interest (%)"
                    type="number"
                    value={inputData.carriedInterest}
                    onChange={handleInputChange('carriedInterest')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Taxa de Hurdle (%)"
                    type="number"
                    value={inputData.hurdleRate}
                    onChange={handleInputChange('hurdleRate')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Retorno Preferencial (%)"
                    type="number"
                    value={inputData.preferredReturn}
                    onChange={handleInputChange('preferredReturn')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={calculateWaterfall}
                    startIcon={<CalculateIcon />}
                  >
                    Calcular
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Visualização do Waterfall */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Visualização do Waterfall"
              avatar={<CalculateIcon />}
            />
            <CardContent>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={results.waterfall}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Resultados Detalhados */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Resultados Detalhados"
              avatar={<CalculateIcon />}
            />
            <CardContent>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Valor ($)</TableCell>
                      <TableCell align="right">Percentual (%)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Retorno Total</TableCell>
                      <TableCell align="right">{inputData.totalReturn.toLocaleString()}</TableCell>
                      <TableCell align="right">100%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Taxa de Gestão</TableCell>
                      <TableCell align="right">{results.managementFeeAmount.toLocaleString()}</TableCell>
                      <TableCell align="right">{inputData.managementFee}%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Retorno Preferencial</TableCell>
                      <TableCell align="right">{results.preferredReturnAmount.toLocaleString()}</TableCell>
                      <TableCell align="right">{inputData.preferredReturn}%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Carried Interest</TableCell>
                      <TableCell align="right">{results.carriedInterestAmount.toLocaleString()}</TableCell>
                      <TableCell align="right">{inputData.carriedInterest}%</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Retorno Líquido</strong></TableCell>
                      <TableCell align="right"><strong>{results.netReturn.toLocaleString()}</strong></TableCell>
                      <TableCell align="right">
                        <strong>
                          {((results.netReturn / inputData.totalReturn) * 100).toFixed(2)}%
                        </strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Ações */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={handleSave}
            >
              Salvar
            </Button>
            <Button
              variant="outlined"
              startIcon={<PrintIcon />}
              onClick={handlePrint}
            >
              Imprimir
            </Button>
            <Button
              variant="contained"
              startIcon={<ShareIcon />}
              onClick={handleShare}
            >
              Compartilhar
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WaterfallCalculator; 