import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger("stockvision.lstm")

class SelfAttentionBlock(nn.Module):
    """
    Multi-Head Attention block that operates over the temporal sequence dimension of the LSTM outputs.
    """
    def __init__(self, embed_dim: int, num_heads: int = 4):
        super(SelfAttentionBlock, self).__init__()
        self.multihead_attn = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        self.layernorm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch, seq_len, embed_dim]
        attn_out, _ = self.multihead_attn(x, x, x)
        # Residual connection + Layer Normalization
        out = self.layernorm(x + attn_out)
        return out

class LSTMAttentionPredictor(nn.Module):
    """
    Bidirectional LSTM with Multi-Head Self-Attention over sequential time-series indicators.
    """
    def __init__(self, input_dim: int = 25, hidden_size: int = 128, num_layers: int = 3, dropout: float = 0.3):
        super(LSTMAttentionPredictor, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Bidirectional LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
            bidirectional=True
        )
        
        # Bidirectional output dimension is 2 * hidden_size
        lstm_out_dim = 2 * hidden_size
        
        # Attention block (4 heads over bidirectional LSTM outputs)
        self.attention = SelfAttentionBlock(embed_dim=lstm_out_dim, num_heads=4)
        
        # Fully connected prediction head
        # Linear -> ReLU -> Dropout -> Linear -> Prediction
        self.fc_head = nn.Sequential(
            nn.Linear(lstm_out_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: [batch_size, seq_len, input_dim]
        lstm_out, _ = self.lstm(x) # shape: [batch_size, seq_len, 2 * hidden_size]
        
        # Apply self-attention
        attn_out = self.attention(lstm_out) # shape: [batch_size, seq_len, 2 * hidden_size]
        
        # Pool temporal dimensions (mean pooling over time axis)
        pooled = torch.mean(attn_out, dim=1) # shape: [batch_size, 2 * hidden_size]
        
        # Final forecasting
        prediction = self.fc_head(pooled) # shape: [batch_size, 1]
        return prediction

def train_lstm_model(
    model: nn.Module,
    train_features: np.ndarray,
    train_targets: np.ndarray,
    val_features: Optional[np.ndarray] = None,
    val_targets: Optional[np.ndarray] = None,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 0.001,
    checkpoint_path: str = "checkpoints/lstm_model.pt"
) -> Tuple[nn.Module, list, list]:
    """
    Fits LSTMAttentionPredictor on custom inputs with early stopping, gradient clipping, and scheduler.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Prep DataLoader
    train_dataset = TensorDataset(torch.tensor(train_features), torch.tensor(train_targets))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_loader = None
    if val_features is not None and val_targets is not None:
        val_dataset = TensorDataset(torch.tensor(val_features), torch.tensor(val_targets))
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    # Save folder
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    
    train_losses = []
    val_losses = []
    
    # Early stopping config
    best_val_loss = float('inf')
    patience = 12
    patience_counter = 0
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            predictions = model(batch_x)
            loss = criterion(predictions, batch_y)
            loss.backward()
            
            # Gradient clipping
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            running_loss += loss.item() * batch_x.size(0)
            
        epoch_train_loss = running_loss / len(train_loader.dataset)
        train_losses.append(epoch_train_loss)
        
        # Validation pass
        epoch_val_loss = 0.0
        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                running_val_loss = 0.0
                for batch_vx, batch_vy in val_loader:
                    batch_vx, batch_vy = batch_vx.to(device), batch_vy.to(device)
                    v_preds = model(batch_vx)
                    v_loss = criterion(v_preds, batch_vy)
                    running_val_loss += v_loss.item() * batch_vx.size(0)
                epoch_val_loss = running_val_loss / len(val_loader.dataset)
                val_losses.append(epoch_val_loss)
                scheduler.step(epoch_val_loss)
        else:
            epoch_val_loss = epoch_train_loss
            val_losses.append(epoch_val_loss)
            
        # Logging
        if (epoch + 1) % 5 == 0 or epoch == 0 or epoch == epochs - 1:
            logger.info(f"Epoch {epoch+1:02d}/{epochs:02d} | Train MSE: {epoch_train_loss:.6f} | Val MSE: {epoch_val_loss:.6f}")
            
        # Check early stopping and checkpointing
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            torch.save(model.state_dict(), checkpoint_path)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered at Epoch {epoch+1}. Best Val Loss: {best_val_loss:.6f}")
                break
                
    # Load best weights
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        
    return model, train_losses, val_losses
