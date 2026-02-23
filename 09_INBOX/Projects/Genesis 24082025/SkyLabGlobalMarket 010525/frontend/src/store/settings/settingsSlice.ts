import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Settings {
  theme: 'light' | 'dark';
  language: string;
  timezone: string;
  currency: string;
  notifications: {
    email: boolean;
    push: boolean;
    sound: boolean;
  };
  trading: {
    defaultQuantity: number;
    defaultLeverage: number;
    stopLossPercentage: number;
    takeProfitPercentage: number;
  };
}

interface SettingsState {
  settings: Settings;
  isLoading: boolean;
  error: string | null;
}

const initialState: SettingsState = {
  settings: {
    theme: 'light',
    language: 'pt-BR',
    timezone: 'America/Sao_Paulo',
    currency: 'BRL',
    notifications: {
      email: true,
      push: true,
      sound: true,
    },
    trading: {
      defaultQuantity: 1,
      defaultLeverage: 1,
      stopLossPercentage: 2,
      takeProfitPercentage: 4,
    },
  },
  isLoading: false,
  error: null,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    fetchSettingsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchSettingsSuccess: (state, action: PayloadAction<Settings>) => {
      state.settings = action.payload;
      state.isLoading = false;
      state.error = null;
    },
    fetchSettingsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    updateSettings: (state, action: PayloadAction<Partial<Settings>>) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    updateTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.settings.theme = action.payload;
    },
    updateLanguage: (state, action: PayloadAction<string>) => {
      state.settings.language = action.payload;
    },
    updateTimezone: (state, action: PayloadAction<string>) => {
      state.settings.timezone = action.payload;
    },
    updateCurrency: (state, action: PayloadAction<string>) => {
      state.settings.currency = action.payload;
    },
    updateNotifications: (state, action: PayloadAction<Partial<Settings['notifications']>>) => {
      state.settings.notifications = { ...state.settings.notifications, ...action.payload };
    },
    updateTradingSettings: (state, action: PayloadAction<Partial<Settings['trading']>>) => {
      state.settings.trading = { ...state.settings.trading, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  fetchSettingsStart,
  fetchSettingsSuccess,
  fetchSettingsFailure,
  updateSettings,
  updateTheme,
  updateLanguage,
  updateTimezone,
  updateCurrency,
  updateNotifications,
  updateTradingSettings,
  clearError,
} = settingsSlice.actions;

export default settingsSlice.reducer; 