import { Middleware } from '@reduxjs/toolkit';
import { RootState } from './store';

export const loggerMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  console.group(action.type);
  console.info('dispatching', action);
  const result = next(action);
  console.log('next state', store.getState());
  console.groupEnd();
  return result;
};

export const errorHandlingMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  if (action.error) {
    console.error('Action error:', action.error);
    // Aqui você pode adicionar lógica adicional para lidar com erros
    // como enviar para um serviço de monitoramento de erros
  }
  return next(action);
}; 