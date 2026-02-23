import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@store/hooks';
import { selectPortfolio } from '@store/portfolio/portfolioSlice';
import { PortfolioSummary } from '@components/portfolio/PortfolioSummary';
import { PortfolioChart } from '@components/charts/PortfolioChart';
import { PortfolioList } from '@components/portfolio/PortfolioList';
import { CreatePortfolioDialog } from '@components/portfolio/CreatePortfolioDialog';
import { setCurrentPortfolio } from '@store/portfolio/portfolioSlice';

export const Portfolio: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { portfolios, currentPortfolio } = useAppSelector(selectPortfolio);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = React.useState(false);

  const handleCreatePortfolio = () => {
    setIsCreateDialogOpen(true);
  };

  const handlePortfolioSelect = (portfolioId: string) => {
    const portfolio = portfolios.find((p) => p.id === portfolioId);
    if (portfolio) {
      dispatch(setCurrentPortfolio(portfolio));
    }
  };

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h4">Portfólios</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreatePortfolio}
        >
          Novo Portfólio
        </Button>
      </Box>

      <Grid container spacing={3}>
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
                Resumo do Portfólio
              </Typography>
              <PortfolioSummary />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Meus Portfólios
              </Typography>
              <PortfolioList
                portfolios={portfolios}
                currentPortfolioId={currentPortfolio?.id}
                onPortfolioSelect={handlePortfolioSelect}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <CreatePortfolioDialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
      />
    </Box>
  );
}; 