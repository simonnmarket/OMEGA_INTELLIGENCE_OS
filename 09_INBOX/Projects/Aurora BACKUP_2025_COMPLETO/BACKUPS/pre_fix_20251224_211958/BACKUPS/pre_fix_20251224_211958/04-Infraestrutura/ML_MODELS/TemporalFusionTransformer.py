'''
TEMPORAL FUSION TRANSFORMER - Modelo de IA para análise temporal
LOCAL: 04-Infraestrutura/ML_MODELS/TemporalFusionTransformer.py
INTEGRAÇÃO: Compatível com estrutura AURORA para previsão financeira
'''

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from typing import Tuple, Optional
import numpy as np

if TORCH_AVAILABLE:
    class TemporalFusionTransformer(nn.Module):
        """
        Implementação do Temporal Fusion Transformer adaptado para trading
        """
        
        def __init__(self, 
                     input_size: int = 10,
                     hidden_size: int = 128,
                     num_heads: int = 8,
                     num_encoder_layers: int = 4,
                     num_decoder_layers: int = 4,
                     dropout: float = 0.1):
            super().__init__()
            
            self.input_size = input_size
            self.hidden_size = hidden_size
            self.num_heads = num_heads
            self.dropout = dropout
            
            # Encoder LSTM
            self.encoder_lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_encoder_layers,
                batch_first=True,
                dropout=dropout if num_encoder_layers > 1 else 0
            )
            
            # Decoder LSTM
            self.decoder_lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_decoder_layers,
                batch_first=True,
                dropout=dropout if num_decoder_layers > 1 else 0
            )
            
            # Multi-head Attention
            self.attention = nn.MultiheadAttention(
                embed_dim=hidden_size,
                num_heads=num_heads,
                dropout=dropout,
                batch_first=True
            )
            
            # Gating mechanisms
            self.gate = nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size),
                nn.Sigmoid()
            )
            
            # Output layers
            self.output_layer = nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.LayerNorm(hidden_size // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_size // 2, 3)  # BUY, SELL, HOLD
            )
        
        def forward(self, 
                    historical_data: torch.Tensor,
                    future_data: Optional[torch.Tensor] = None,
                    static_data: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
            """Forward pass do TFT"""
            batch_size, seq_len, _ = historical_data.shape
            
            # Encoder processing
            encoded, (hidden, cell) = self.encoder_lstm(historical_data)
            
            # Prepare decoder input
            if future_data is not None:
                decoder_input = future_data
            else:
                decoder_input = historical_data[:, -1:, :].repeat(1, 1, 1)
            
            # Decoder processing
            decoded, _ = self.decoder_lstm(decoder_input, (hidden, cell))
            
            # Attention mechanism
            attended, attention_weights = self.attention(
                decoded, encoded, encoded,
                need_weights=True
            )
            
            # Gated fusion
            gate_values = self.gate(torch.cat([decoded, attended], dim=-1))
            gated_output = gate_values * decoded + (1 - gate_values) * attended
            
            # Output layer
            output = self.output_layer(gated_output)
            probabilities = F.softmax(output, dim=-1)
            
            return probabilities, attention_weights
        
        def predict_trading_signal(self, 
                                  market_data: torch.Tensor,
                                  confidence_threshold: float = 0.6) -> dict:
            """Prediz sinal de trading"""
            self.eval()
            
            with torch.no_grad():
                probabilities, attention_weights = self.forward(market_data)
                last_probs = probabilities[0, -1, :]
                action_idx = torch.argmax(last_probs).item()
                confidence = last_probs[action_idx].item()
                
                actions = ["BUY", "SELL", "HOLD"]
                action = actions[action_idx]
                
                if confidence < confidence_threshold:
                    action = "HOLD"
                    confidence = last_probs[2].item()
                
                return {
                    'action': action,
                    'confidence': confidence,
                    'probabilities': {
                        'BUY': last_probs[0].item(),
                        'SELL': last_probs[1].item(),
                        'HOLD': last_probs[2].item()
                    },
                    'model_used': 'TemporalFusionTransformer',
                    'timestamp': '2025-12-17'
                }
else:
    # Fallback se PyTorch não estiver disponível
    class TemporalFusionTransformer:
        def __init__(self, *args, **kwargs):
            pass
        
        def predict_trading_signal(self, *args, **kwargs):
            return {
                'action': 'HOLD',
                'confidence': 0.5,
                'error': 'PyTorch não disponível - instale: pip install torch'
            }

def create_tft_model(input_features: int = 10, device: str = 'cpu') -> TemporalFusionTransformer:
    """Cria e configura modelo TFT"""
    if TORCH_AVAILABLE:
        model = TemporalFusionTransformer(
            input_size=input_features,
            hidden_size=128,
            num_heads=8,
            num_encoder_layers=2,
            num_decoder_layers=2,
            dropout=0.1
        )
        model.to(device)
        return model
    else:
        return TemporalFusionTransformer()

