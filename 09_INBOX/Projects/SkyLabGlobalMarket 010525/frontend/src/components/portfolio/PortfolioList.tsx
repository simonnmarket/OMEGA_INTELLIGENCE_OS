import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemSecondaryAction,
  Typography,
  IconButton,
  useTheme,
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { useAppDispatch } from '@store/hooks';
import { deletePortfolio } from '@store/portfolio/portfolioSlice';

interface PortfolioListProps {
  portfolios: Array<{
    id: string;
    name: string;
    totalValue: number;
  }>;
  currentPortfolioId?: string;
  onPortfolioSelect: (portfolioId: string) => void;
}

export const PortfolioList: React.FC<PortfolioListProps> = ({
  portfolios,
  currentPortfolioId,
  onPortfolioSelect,
}) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();

  const handleDeletePortfolio = async (portfolioId: string) => {
    try {
      await dispatch(deletePortfolio(portfolioId)).unwrap();
    } catch (error) {
      console.error('Erro ao excluir portfólio:', error);
    }
  };

  return (
    <Box>
      {portfolios.length === 0 ? (
        <Typography color="text.secondary" align="center">
          Nenhum portfólio encontrado
        </Typography>
      ) : (
        <List>
          {portfolios.map((portfolio) => (
            <ListItem
              key={portfolio.id}
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleDeletePortfolio(portfolio.id)}
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemButton
                selected={portfolio.id === currentPortfolioId}
                onClick={() => onPortfolioSelect(portfolio.id)}
              >
                <ListItemText
                  primary={portfolio.name}
                  secondary={
                    <Typography variant="body2" color="text.secondary">
                      {portfolio.totalValue.toLocaleString('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                      })}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}; 