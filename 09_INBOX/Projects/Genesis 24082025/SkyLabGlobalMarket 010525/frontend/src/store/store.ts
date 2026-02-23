import { configureStore } from '@reduxjs/toolkit';
import portfolioReducer from './portfolio/portfolioSlice';
import tradingReducer from './trading/tradingSlice';
import userReducer from './user/userSlice';

export const store = configureStore({
  reducer: {
    portfolio: portfolioReducer,
    trading: tradingReducer,
    user: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 