import { RootState } from './store';
import { Asset, Position, Trade, Portfolio, User } from './types';

export const selectPortfolio = (state: RootState) => state.portfolio;
export const selectTrading = (state: RootState) => state.trading;
export const selectUser = (state: RootState) => state.user;

export const selectPortfolios = (state: RootState): Portfolio[] =>
  state.portfolio.portfolios;

export const selectCurrentPortfolio = (state: RootState): Portfolio | null =>
  state.portfolio.currentPortfolio;

export const selectAvailableAssets = (state: RootState): Asset[] =>
  state.trading.availableAssets;

export const selectSelectedAsset = (state: RootState): Asset | null =>
  state.trading.selectedAsset;

export const selectPositions = (state: RootState): Position[] =>
  state.trading.positions;

export const selectRecentTrades = (state: RootState): Trade[] =>
  state.trading.recentTrades;

export const selectUserData = (state: RootState): User | null =>
  state.user.user;

export const selectUserSettings = (state: RootState) =>
  state.user.user?.settings;

export const selectIsLoading = (state: RootState): boolean =>
  state.portfolio.isLoading ||
  state.trading.isLoading ||
  state.user.isLoading;

export const selectError = (state: RootState): string | null =>
  state.portfolio.error || state.trading.error || state.user.error; 