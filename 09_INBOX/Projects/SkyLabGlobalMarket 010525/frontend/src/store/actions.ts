import { createAction } from '@reduxjs/toolkit';
import { Asset, Position, Trade, Portfolio, User } from './types';

// Portfolio Actions
export const setCurrentPortfolio = createAction<Portfolio>('portfolio/setCurrentPortfolio');
export const clearCurrentPortfolio = createAction('portfolio/clearCurrentPortfolio');

// Trading Actions
export const setSelectedAsset = createAction<Asset>('trading/setSelectedAsset');
export const clearSelectedAsset = createAction('trading/clearSelectedAsset');
export const addPosition = createAction<Position>('trading/addPosition');
export const removePosition = createAction<string>('trading/removePosition');
export const updatePosition = createAction<Position>('trading/updatePosition');
export const addTrade = createAction<Trade>('trading/addTrade');

// User Actions
export const setUser = createAction<User>('user/setUser');
export const clearUser = createAction('user/clearUser');
export const updateUserSettings = createAction<Partial<User['settings']>>('user/updateUserSettings');

// Error Actions
export const setError = createAction<string>('error/setError');
export const clearError = createAction('error/clearError');

// Loading Actions
export const setLoading = createAction<boolean>('loading/setLoading'); 