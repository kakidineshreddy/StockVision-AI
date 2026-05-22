import os
import math
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger("stockvision.transformer")

class PositionalEncoding(nn.Module):
    """
    Standard Positional Encoding for time-series sequences.
    """
    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0) # shape: [1, max_len, d_model]
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch_size, seq_len, d_model]
        x = x + self.pe[:, :x.size(1)]
        return x

class TransformerTimeSeriesPredictor(nn.Module):
    """
    Transformer Encoder architecture for multi-feature sequence prediction.
    Features: Positional Encoding, 4 Encoder Layers, 8 Attention Heads, 256 Model Dim.
    """
    def __init__(self, input_dim: int = 25, d_model: int = 256, nhead: int = 8, num_layers: int = 4, dim_feedforward: int = 512, dropout: float = 0.2):
        super(TransformerTimeSeriesPredictor, self).__init__()
        
        # Projection linear layer: projects 25 features to 256 model dimension
        self.input_projection = nn.Linear(input_dim, d_model)
        
        self.pos_encoder = PositionalEncoding(d_model=d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output prediction head: maps sequential latent variables to next-day prediction
        self.fc_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )
        
    def _generate_square_subsequent_mask(self, sz: int, device: torch.device) -> torch.Tensor:
        """Generates a causal mask to prevent attention from seeing future steps."""
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask.to(device)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input shape: [batch_size, seq_len, input_dim]
        device = x.device
        seq_len = x.size(1)
        
        # 1. Project input features to model dimension
        x = self.input_projection(x) # shape: [batch_size, seq_len, d_model]
        
        # 2. Add Positional Encoding
        x = self.pos_encoder(x)
        
        # 3. Create causal mask for autoregressive safety
        mask = self._generate_square_subsequent_mask(seq_len, device)
        
        # 4. Pass through Transformer encoder layers
        encoder_out = self.transformer_encoder(x, mask=mask) # shape: [batch_size, seq_len, d_model]
        
        # 5. Pool temporal info (take last sequence state as query summarize representation)
        last_timestep = encoder_out[:, -1, :] # shape: [batch_size, d_model]
        
        # 6. Final forecast
        prediction = self.fc_head(last_timestep) # shape: [batch_size, 1]
        return prediction

def train_transformer_model(
    model: nn.Module,
    train_features: np.ndarray,
    train_targets: np.ndarray,
    val_features: Optional[np.ndarray] = None,
    val_targets: Optional[np.ndarray] = None,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 0.0005,
    checkpoint_path: str = "checkpoints/transformer_model.pt"
) -> Tuple[nn.Module, list, list]:
    """
    Fits TransformerTimeSeriesPredictor on custom inputs with early stopping and learning rate updates.
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
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
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
