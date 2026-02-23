export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';

export const ASSET_TYPES = {
  STOCK: 'stock',
  CRYPTO: 'crypto',
  FOREX: 'forex',
  COMMODITY: 'commodity',
} as const;

export const POSITION_TYPES = {
  BUY: 'buy',
  SELL: 'sell',
} as const;

export const ORDER_TYPES = {
  MARKET: 'market',
  LIMIT: 'limit',
  STOP: 'stop',
  STOP_LIMIT: 'stop_limit',
} as const;

export const TIME_FRAMES = {
  MINUTE_1: '1m',
  MINUTE_5: '5m',
  MINUTE_15: '15m',
  MINUTE_30: '30m',
  HOUR_1: '1h',
  HOUR_4: '4h',
  DAY_1: '1d',
  WEEK_1: '1w',
  MONTH_1: '1M',
} as const;

export const DEFAULT_PORTFOLIO_NAME = 'Portfólio Principal';

export const DEFAULT_USER_SETTINGS = {
  notifications: true,
  darkMode: false,
} as const;

export const ERROR_MESSAGES = {
  FETCH_ERROR: 'Erro ao buscar dados',
  CREATE_ERROR: 'Erro ao criar registro',
  UPDATE_ERROR: 'Erro ao atualizar registro',
  DELETE_ERROR: 'Erro ao excluir registro',
  NETWORK_ERROR: 'Erro de conexão',
  AUTH_ERROR: 'Erro de autenticação',
  VALIDATION_ERROR: 'Erro de validação',
} as const;

export const SUCCESS_MESSAGES = {
  CREATE_SUCCESS: 'Registro criado com sucesso',
  UPDATE_SUCCESS: 'Registro atualizado com sucesso',
  DELETE_SUCCESS: 'Registro excluído com sucesso',
} as const; 