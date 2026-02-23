import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from '../store';

interface Asset {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  totalValue: number;
  profitLoss: number;
  profitLossPercentage: number;
}

interface Portfolio {
  id: string;
  name: string;
  description: string;
  assets: Asset[];
  totalValue: number;
  totalProfitLoss: number;
  totalProfitLossPercentage: number;
  createdAt: string;
  updatedAt: string;
}

interface PortfolioState {
  portfolios: Portfolio[];
  currentPortfolio: Portfolio | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  portfolios: [],
  currentPortfolio: null,
  isLoading: false,
  error: null,
};

export const fetchPortfolios = createAsyncThunk(
  'portfolio/fetchPortfolios',
  async () => {
    const response = await fetch('/api/portfolios');
    if (!response.ok) {
      throw new Error('Erro ao buscar portfólios');
    }
    return response.json();
  }
);

export const createPortfolio = createAsyncThunk(
  'portfolio/createPortfolio',
  async (portfolioData: { name: string; initialValue: number }) => {
    const response = await fetch('/api/portfolios', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(portfolioData),
    });

    if (!response.ok) {
      throw new Error('Erro ao criar portfólio');
    }

    return response.json();
  }
);

export const deletePortfolio = createAsyncThunk(
  'portfolio/deletePortfolio',
  async (portfolioId: string) => {
    const response = await fetch(`/api/portfolios/${portfolioId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Erro ao excluir portfólio');
    }

    return portfolioId;
  }
);

export const updatePortfolio = createAsyncThunk(
  'portfolio/updatePortfolio',
  async (portfolioData: { id: string; name: string; totalValue: number }) => {
    const response = await fetch(`/api/portfolios/${portfolioData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(portfolioData),
    });

    if (!response.ok) {
      throw new Error('Erro ao atualizar portfólio');
    }

    return response.json();
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setCurrentPortfolio: (state, action) => {
      state.currentPortfolio = action.payload;
    },
    addPortfolio: (state, action) => {
      state.portfolios.push(action.payload);
    },
    updatePortfolio: (state, action) => {
      const index = state.portfolios.findIndex((p) => p.id === action.payload.id);
      if (index !== -1) {
        state.portfolios[index] = action.payload;
      }
    },
    deletePortfolio: (state, action) => {
      state.portfolios = state.portfolios.filter((p) => p.id !== action.payload);
      if (state.currentPortfolio?.id === action.payload) {
        state.currentPortfolio = null;
      }
    },
    addAsset: (state, action) => {
      const portfolio = state.portfolios.find((p) => p.id === action.payload.portfolioId);
      if (portfolio) {
        portfolio.assets.push(action.payload.asset);
        if (state.currentPortfolio?.id === portfolio.id) {
          state.currentPortfolio = portfolio;
        }
      }
    },
    updateAsset: (state, action) => {
      const portfolio = state.portfolios.find((p) => p.id === action.payload.portfolioId);
      if (portfolio) {
        const index = portfolio.assets.findIndex((a) => a.id === action.payload.asset.id);
        if (index !== -1) {
          portfolio.assets[index] = action.payload.asset;
          if (state.currentPortfolio?.id === portfolio.id) {
            state.currentPortfolio = portfolio;
          }
        }
      }
    },
    deleteAsset: (state, action) => {
      const portfolio = state.portfolios.find((p) => p.id === action.payload.portfolioId);
      if (portfolio) {
        portfolio.assets = portfolio.assets.filter((a) => a.id !== action.payload.assetId);
        if (state.currentPortfolio?.id === portfolio.id) {
          state.currentPortfolio = portfolio;
        }
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolios.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolios.fulfilled, (state, action) => {
        state.portfolios = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchPortfolios.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao buscar portfólios';
      })
      .addCase(createPortfolio.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createPortfolio.fulfilled, (state, action) => {
        state.portfolios.push(action.payload);
        state.currentPortfolio = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(createPortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao criar portfólio';
      })
      .addCase(deletePortfolio.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deletePortfolio.fulfilled, (state, action) => {
        state.portfolios = state.portfolios.filter(
          (portfolio) => portfolio.id !== action.payload
        );
        if (state.currentPortfolio?.id === action.payload) {
          state.currentPortfolio = null;
        }
        state.isLoading = false;
        state.error = null;
      })
      .addCase(deletePortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao excluir portfólio';
      })
      .addCase(updatePortfolio.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updatePortfolio.fulfilled, (state, action) => {
        const index = state.portfolios.findIndex(
          (portfolio) => portfolio.id === action.payload.id
        );
        if (index !== -1) {
          state.portfolios[index] = action.payload;
        }
        if (state.currentPortfolio?.id === action.payload.id) {
          state.currentPortfolio = action.payload;
        }
        state.isLoading = false;
        state.error = null;
      })
      .addCase(updatePortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao atualizar portfólio';
      });
  },
});

export const { setCurrentPortfolio, addPortfolio, updatePortfolio, deletePortfolio, addAsset, updateAsset, deleteAsset, clearError } = portfolioSlice.actions;

export const selectPortfolio = (state: RootState) => state.portfolio;

export default portfolioSlice.reducer; 