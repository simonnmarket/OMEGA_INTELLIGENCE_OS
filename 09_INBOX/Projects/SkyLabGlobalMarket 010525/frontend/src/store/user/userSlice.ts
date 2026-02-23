import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from '../store';

interface UserSettings {
  notifications: boolean;
  darkMode: boolean;
}

interface User {
  id: string;
  name: string;
  email: string;
  settings: UserSettings;
}

interface UserState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: UserState = {
  user: null,
  isLoading: false,
  error: null,
};

export const fetchUser = createAsyncThunk('user/fetchUser', async () => {
  const response = await fetch('/api/user');
  if (!response.ok) {
    throw new Error('Erro ao buscar dados do usuário');
  }
  return response.json();
});

export const updateUserSettings = createAsyncThunk(
  'user/updateUserSettings',
  async (settings: Partial<UserSettings>) => {
    const response = await fetch('/api/user/settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error('Erro ao atualizar configurações');
    }

    return response.json();
  }
);

export const updateUserProfile = createAsyncThunk(
  'user/updateUserProfile',
  async (profileData: { name: string; email: string }) => {
    const response = await fetch('/api/user/profile', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error('Erro ao atualizar perfil');
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
    const response = await fetch('/api/user/password', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(passwordData),
    });

    if (!response.ok) {
      throw new Error('Erro ao atualizar senha');
    }

    return response.json();
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao buscar dados do usuário';
      })
      .addCase(updateUserSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserSettings.fulfilled, (state, action) => {
        if (state.user) {
          state.user.settings = {
            ...state.user.settings,
            ...action.payload,
          };
        }
        state.isLoading = false;
        state.error = null;
      })
      .addCase(updateUserSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao atualizar configurações';
      })
      .addCase(updateUserProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        if (state.user) {
          state.user.name = action.payload.name;
          state.user.email = action.payload.email;
        }
        state.isLoading = false;
        state.error = null;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao atualizar perfil';
      })
      .addCase(updateUserPassword.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserPassword.fulfilled, (state) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(updateUserPassword.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Erro ao atualizar senha';
      });
  },
});

export const selectUser = (state: RootState) => state.user;

export default userSlice.reducer; 