import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  useTheme,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { useAppDispatch } from '@store/hooks';
import { createPortfolio } from '@store/portfolio/portfolioSlice';
import { toast } from 'react-toastify';

interface CreatePortfolioDialogProps {
  open: boolean;
  onClose: () => void;
}

const validationSchema = yup.object({
  name: yup.string().required('Nome é obrigatório'),
  initialValue: yup
    .number()
    .min(0, 'O valor inicial deve ser maior ou igual a zero')
    .required('Valor inicial é obrigatório'),
});

export const CreatePortfolioDialog: React.FC<CreatePortfolioDialogProps> = ({
  open,
  onClose,
}) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();

  const formik = useFormik({
    initialValues: {
      name: '',
      initialValue: 0,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await dispatch(createPortfolio(values)).unwrap();
        toast.success('Portfólio criado com sucesso!');
        onClose();
      } catch (error) {
        toast.error('Erro ao criar portfólio. Tente novamente.');
      }
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={formik.handleSubmit}>
        <DialogTitle>Criar Novo Portfólio</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            name="name"
            label="Nome do Portfólio"
            type="text"
            fullWidth
            value={formik.values.name}
            onChange={formik.handleChange}
            error={formik.touched.name && Boolean(formik.errors.name)}
            helperText={formik.touched.name && formik.errors.name}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            id="initialValue"
            name="initialValue"
            label="Valor Inicial"
            type="number"
            fullWidth
            value={formik.values.initialValue}
            onChange={formik.handleChange}
            error={formik.touched.initialValue && Boolean(formik.errors.initialValue)}
            helperText={formik.touched.initialValue && formik.errors.initialValue}
            InputProps={{
              startAdornment: 'R$',
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancelar</Button>
          <Button type="submit" variant="contained" color="primary">
            Criar
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}; 