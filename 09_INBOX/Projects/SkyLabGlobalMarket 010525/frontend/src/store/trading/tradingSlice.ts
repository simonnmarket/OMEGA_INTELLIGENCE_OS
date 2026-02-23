import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from '../store';

interface Asset {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
}

interface Position {
  id: string;
  asset: Asset;
  type: 'buy' | 'sell';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  profitLoss: number;
  profitLossPercentage: number;
  createdAt: string;
  updatedAt: string;
}

interface Trade {
  id: string;
  asset: Asset;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  date: string;
}

interface TradingState {
  availableAssets: Asset[];
  selectedAsset: Asset | null;
  positions: Position[];
  recentTrades: Trade[];
  isLoading: boolean;
  error: string | null;
}

const initialState: TradingState = {
  availableAssets: [],
  selectedAsset: null,
  positions: [],
  recentTrades: [],
  isLoading: false,
  error: null,
};

export const fetchAvailableAssets = createAsyncThunk(
  'trading/fetchAvailableAssets',
  async () => {
    const response = await fetch('/api/assets');
    if (!response.ok) {
      throw new Error('Erro ao buscar ativos disponíveis');
    }
    return response.json();
  }
);

export const createPosition = createAsyncThunk(
  'trading/createPosition',
  async (positionData: {
    assetId: string;
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
  }) => {
    const response = await fetch('/api/positions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(positionData),
    });

    if (!response.ok) {
      throw new Error('Erro ao criar posição');
    }

    return response.json();
  }
);

export const closePosition = createAsyncThunk(
  'trading/closePosition',
  async (positionId: string) => {
    const response = await fetch(`/api/positions/${positionId}/close`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Erro ao fechar posição');
    }

    return positionId;
  }
);

export const fetchPositions = createAsyncThunk(
  'trading/fetchPositions',
  async () => {
    const response = await fetch('/api/positions');
    if (!response.ok) {
      throw new Error('Erro ao buscar posições');
    }
    return response.json();
  }
);

export const fetchRecentTrades = createAsyncThunk(
  'trading/fetchRecentTrades',
  async () => {
    const response = await fetch('/api/trades/recent');
    if (!response.ok) {
      throw new Error('Erro ao buscar operações recentes');
    }
    return response.json();
  }
);

const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    setSelectedAsset: (state, action) => {
      state.selectedAsset = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAvailableAssets.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAvailableAssets.fulfilled, (state, action) => {
        state.availableAssets = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchAvailableAssets.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao buscar ativos disponíveis';
      })
      .addCase(createPosition.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createPosition.fulfilled, (state, action) => {
        state.positions.push(action.payload);
        state.isLoading = false;
        state.error = null;
      })
      .addCase(createPosition.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao criar posição';
      })
      .addCase(closePosition.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(closePosition.fulfilled, (state, action) => {
        state.positions = state.positions.filter(
          (position) => position.id !== action.payload
        );
        state.isLoading = false;
        state.error = null;
      })
      .addCase(closePosition.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao fechar posição';
      })
      .addCase(fetchPositions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPositions.fulfilled, (state, action) => {
        state.positions = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchPositions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao buscar posições';
      })
      .addCase(fetchRecentTrades.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchRecentTrades.fulfilled, (state, action) => {
        state.recentTrades = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchRecentTrades.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao buscar operações recentes';
      });
  },
});

export const { setSelectedAsset } = tradingSlice.actions;

export const selectTrading = (state: RootState) => state.trading;

export default tradingSlice.reducer; 