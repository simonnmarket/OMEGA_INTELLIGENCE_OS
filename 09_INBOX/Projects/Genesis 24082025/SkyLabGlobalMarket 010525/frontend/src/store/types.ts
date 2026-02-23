export interface Asset {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
}

export interface Position {
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

export interface Trade {
  id: string;
  asset: Asset;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  date: string;
}

export interface Portfolio {
  id: string;
  name: string;
  totalValue: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserSettings {
  notifications: boolean;
  darkMode: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  settings: UserSettings;
} 