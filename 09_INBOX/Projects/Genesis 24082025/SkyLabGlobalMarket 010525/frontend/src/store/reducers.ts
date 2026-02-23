import { createReducer } from '@reduxjs/toolkit';
import { Asset, Position, Trade, Portfolio, User } from './types';
import {
  setCurrentPortfolio,
  clearCurrentPortfolio,
  setSelectedAsset,
  clearSelectedAsset,
  addPosition,
  removePosition,
  updatePosition,
  addTrade,
  setUser,
  clearUser,
  updateUserSettings,
  setError,
  clearError,
  setLoading,
} from './actions';

interface PortfolioState {
  portfolios: Portfolio[];
  currentPortfolio: Portfolio | null;
  isLoading: boolean;
  error: string | null;
}

interface TradingState {
  availableAssets: Asset[];
  selectedAsset: Asset | null;
  positions: Position[];
  recentTrades: Trade[];
  isLoading: boolean;
  error: string | null;
}

interface UserState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

const initialPortfolioState: PortfolioState = {
  portfolios: [],
  currentPortfolio: null,
  isLoading: false,
  error: null,
};

const initialTradingState: TradingState = {
  availableAssets: [],
  selectedAsset: null,
  positions: [],
  recentTrades: [],
  isLoading: false,
  error: null,
};

const initialUserState: UserState = {
  user: null,
  isLoading: false,
  error: null,
};

export const portfolioReducer = createReducer(initialPortfolioState, (builder) => {
  builder
    .addCase(setCurrentPortfolio, (state, action) => {
      state.currentPortfolio = action.payload;
    })
    .addCase(clearCurrentPortfolio, (state) => {
      state.currentPortfolio = null;
    })
    .addCase(setLoading, (state, action) => {
      state.isLoading = action.payload;
    })
    .addCase(setError, (state, action) => {
      state.error = action.payload;
    })
    .addCase(clearError, (state) => {
      state.error = null;
    });
});

export const tradingReducer = createReducer(initialTradingState, (builder) => {
  builder
    .addCase(setSelectedAsset, (state, action) => {
      state.selectedAsset = action.payload;
    })
    .addCase(clearSelectedAsset, (state) => {
      state.selectedAsset = null;
    })
    .addCase(addPosition, (state, action) => {
      state.positions.push(action.payload);
    })
    .addCase(removePosition, (state, action) => {
      state.positions = state.positions.filter(
        (position) => position.id !== action.payload
      );
    })
    .addCase(updatePosition, (state, action) => {
      const index = state.positions.findIndex(
        (position) => position.id === action.payload.id
      );
      if (index !== -1) {
        state.positions[index] = action.payload;
      }
    })
    .addCase(addTrade, (state, action) => {
      state.recentTrades.unshift(action.payload);
      if (state.recentTrades.length > 10) {
        state.recentTrades.pop();
      }
    })
    .addCase(setLoading, (state, action) => {
      state.isLoading = action.payload;
    })
    .addCase(setError, (state, action) => {
      state.error = action.payload;
    })
    .addCase(clearError, (state) => {
      state.error = null;
    });
});

export const userReducer = createReducer(initialUserState, (builder) => {
  builder
    .addCase(setUser, (state, action) => {
      state.user = action.payload;
    })
    .addCase(clearUser, (state) => {
      state.user = null;
    })
    .addCase(updateUserSettings, (state, action) => {
      if (state.user) {
        state.user.settings = {
          ...state.user.settings,
          ...action.payload,
        };
      }
    })
    .addCase(setLoading, (state, action) => {
      state.isLoading = action.payload;
    })
    .addCase(setError, (state, action) => {
      state.error = action.payload;
    })
    .addCase(clearError, (state) => {
      state.error = null;
    });
}); 