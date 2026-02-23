import { createAsyncThunk } from '@reduxjs/toolkit';
import { API_BASE_URL, ERROR_MESSAGES } from './constants';
import { Asset, Position, Trade, Portfolio, User } from './types';

// Portfolio Thunks
export const fetchPortfolios = createAsyncThunk(
  'portfolio/fetchPortfolios',
  async () => {
    const response = await fetch(`${API_BASE_URL}/portfolios`);
    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.FETCH_ERROR);
    }
    return response.json();
  }
);

export const createPortfolio = createAsyncThunk(
  'portfolio/createPortfolio',
  async (portfolioData: { name: string; initialValue: number }) => {
    const response = await fetch(`${API_BASE_URL}/portfolios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(portfolioData),
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.CREATE_ERROR);
    }

    return response.json();
  }
);

export const deletePortfolio = createAsyncThunk(
  'portfolio/deletePortfolio',
  async (portfolioId: string) => {
    const response = await fetch(`${API_BASE_URL}/portfolios/${portfolioId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.DELETE_ERROR);
    }

    return portfolioId;
  }
);

// Trading Thunks
export const fetchAvailableAssets = createAsyncThunk(
  'trading/fetchAvailableAssets',
  async () => {
    const response = await fetch(`${API_BASE_URL}/assets`);
    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.FETCH_ERROR);
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
    const response = await fetch(`${API_BASE_URL}/positions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(positionData),
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.CREATE_ERROR);
    }

    return response.json();
  }
);

export const closePosition = createAsyncThunk(
  'trading/closePosition',
  async (positionId: string) => {
    const response = await fetch(`${API_BASE_URL}/positions/${positionId}/close`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.UPDATE_ERROR);
    }

    return positionId;
  }
);

export const fetchPositions = createAsyncThunk(
  'trading/fetchPositions',
  async () => {
    const response = await fetch(`${API_BASE_URL}/positions`);
    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.FETCH_ERROR);
    }
    return response.json();
  }
);

export const fetchRecentTrades = createAsyncThunk(
  'trading/fetchRecentTrades',
  async () => {
    const response = await fetch(`${API_BASE_URL}/trades/recent`);
    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.FETCH_ERROR);
    }
    return response.json();
  }
);

// User Thunks
export const fetchUser = createAsyncThunk('user/fetchUser', async () => {
  const response = await fetch(`${API_BASE_URL}/user`);
  if (!response.ok) {
    throw new Error(ERROR_MESSAGES.FETCH_ERROR);
  }
  return response.json();
});

export const updateUserSettings = createAsyncThunk(
  'user/updateUserSettings',
  async (settings: Partial<User['settings']>) => {
    const response = await fetch(`${API_BASE_URL}/user/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.UPDATE_ERROR);
    }

    return response.json();
  }
);

export const updateUserProfile = createAsyncThunk(
  'user/updateUserProfile',
  async (profileData: { name: string; email: string }) => {
    const response = await fetch(`${API_BASE_URL}/user/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.UPDATE_ERROR);
    }

    return response.json();
  }
);

export const updateUserPassword = createAsyncThunk(
  'user/updateUserPassword',
  async (passwordData: {
    currentPassword: string;
    newPassword: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/user/password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(passwordData),
    });

    if (!response.ok) {
      throw new Error(ERROR_MESSAGES.UPDATE_ERROR);
    }

    return response.json();
  }
); 