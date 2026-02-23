import React from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  useTheme,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import { selectTrading } from '@store/trading/tradingSlice';
import { createPosition } from '@store/trading/tradingSlice';
import { toast } from 'react-toastify';

const validationSchema = yup.object({
  assetId: yup.string().required('Ativo é obrigatório'),
  type: yup.string().required('Tipo de operação é obrigatório'),
  quantity: yup
    .number()
    .min(1, 'A quantidade deve ser maior que zero')
    .required('Quantidade é obrigatória'),
  price: yup
    .number()
    .min(0.01, 'O preço deve ser maior que zero')
    .required('Preço é obrigatório'),
});

export const TradingForm: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { availableAssets } = useAppSelector(selectTrading);

  const formik = useFormik({
    initialValues: {
      assetId: '',
      type: 'buy',
      quantity: 0,
      price: 0,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await dispatch(createPosition(values)).unwrap();
        toast.success('Operação realizada com sucesso!');
        formik.resetForm();
      } catch (error) {
        toast.error('Erro ao realizar operação. Tente novamente.');
      }
    },
  });

  return (
    <Box component="form" onSubmit={formik.handleSubmit}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel id="asset-label">Ativo</InputLabel>
            <Select
              labelId="asset-label"
              id="assetId"
              name="assetId"
              value={formik.values.assetId}
              onChange={formik.handleChange}
              error={formik.touched.assetId && Boolean(formik.errors.assetId)}
            >
              {availableAssets.map((asset) => (
                <MenuItem key={asset.id} value={asset.id}>
                  {asset.symbol} - {asset.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel id="type-label">Tipo de Operação</InputLabel>
            <Select
              labelId="type-label"
              id="type"
              name="type"
              value={formik.values.type}
              onChange={formik.handleChange}
              error={formik.touched.type && Boolean(formik.errors.type)}
            >
              <MenuItem value="buy">Compra</MenuItem>
              <MenuItem value="sell">Venda</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            id="quantity"
            name="quantity"
            label="Quantidade"
            type="number"
            value={formik.values.quantity}
            onChange={formik.handleChange}
            error={formik.touched.quantity && Boolean(formik.errors.quantity)}
            helperText={formik.touched.quantity && formik.errors.quantity}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            id="price"
            name="price"
            label="Preço"
            type="number"
            value={formik.values.price}
            onChange={formik.handleChange}
            error={formik.touched.price && Boolean(formik.errors.price)}
            helperText={formik.touched.price && formik.errors.price}
            InputProps={{
              startAdornment: 'R$',
            }}
          />
        </Grid>

        <Grid item xs={12}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={formik.isSubmitting}
          >
            {formik.values.type === 'buy' ? 'Comprar' : 'Vender'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}; 