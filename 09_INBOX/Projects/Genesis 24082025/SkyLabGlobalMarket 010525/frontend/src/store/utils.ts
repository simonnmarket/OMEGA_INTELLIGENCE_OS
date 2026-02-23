import { Asset, Position, Trade, Portfolio } from './types';

export const calculatePositionProfitLoss = (position: Position): number => {
  const priceDifference = position.currentPrice - position.entryPrice;
  return position.type === 'buy' ? priceDifference * position.quantity : -priceDifference * position.quantity;
};

export const calculatePositionProfitLossPercentage = (position: Position): number => {
  const profitLoss = calculatePositionProfitLoss(position);
  return (profitLoss / (position.entryPrice * position.quantity)) * 100;
};

export const calculatePortfolioTotalValue = (portfolio: Portfolio, positions: Position[]): number => {
  return positions.reduce((total, position) => {
    return total + (position.currentPrice * position.quantity);
  }, 0);
};

export const calculatePortfolioProfitLoss = (positions: Position[]): number => {
  return positions.reduce((total, position) => {
    return total + calculatePositionProfitLoss(position);
  }, 0);
};

export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

export const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const sortPositionsByProfitLoss = (positions: Position[]): Position[] => {
  return [...positions].sort((a, b) => {
    const profitLossA = calculatePositionProfitLoss(a);
    const profitLossB = calculatePositionProfitLoss(b);
    return profitLossB - profitLossA;
  });
};

export const filterPositionsByAsset = (positions: Position[], assetId: string): Position[] => {
  return positions.filter(position => position.asset.id === assetId);
};

export const getAssetPositions = (positions: Position[], assetId: string): Position[] => {
  return positions.filter(position => position.asset.id === assetId);
};

export const getAssetTotalQuantity = (positions: Position[], assetId: string): number => {
  return positions.reduce((total, position) => {
    if (position.asset.id === assetId) {
      return position.type === 'buy' ? total + position.quantity : total - position.quantity;
    }
    return total;
  }, 0);
};

export const getAssetAveragePrice = (positions: Position[], assetId: string): number => {
  const assetPositions = getAssetPositions(positions, assetId);
  if (assetPositions.length === 0) return 0;

  const totalValue = assetPositions.reduce((total, position) => {
    return total + (position.entryPrice * position.quantity);
  }, 0);

  const totalQuantity = getAssetTotalQuantity(positions, assetId);
  return totalValue / totalQuantity;
}; 