"""CLI script for model training driven by Hydra configuration."""

from __future__ import annotations

import sys
from pathlib import Path

import hydra
import numpy as np
import torch
from loguru import logger
from omegaconf import DictConfig, OmegaConf
from torch.utils.data import DataLoader

from datasets.base import ClimateTimeSeriesDataset
from datasets.registry import DatasetRegistry
from models.registry import ModelRegistry
from training.experiment import ExperimentManager
from training.trainer import ClimateTrainer


@hydra.main(version_base="1.3", config_path="../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    """Main training execution entrypoint."""
    logger.info("Initializing Gaia Training CLI...")
    logger.info(f"\n{OmegaConf.to_yaml(cfg)}")

    # 1. Setup reproducibility and tracking
    exp = ExperimentManager(cfg).setup()
    exp.log_config()

    # 2. Instantiate Dataset Loader
    dataset_name = cfg.dataset.name
    logger.info(f"Loading climate dataset loader: {dataset_name}")
    loader_obj = DatasetRegistry.create(cfg.dataset)
    raw_ds = loader_obj.load_raw(cfg.paths.data_dir)
    proc_ds = loader_obj.preprocess(raw_ds)

    # 3. Create synthetic feature matrix and labels for demonstration
    # In full training, this extracts precomputed features from feature_engineering/
    n_steps = len(proc_ds.time)
    n_features = cfg.model.architecture.input_dim
    
    # Generate realistic features with increasing variance/AR(1)
    rng = np.random.default_rng(cfg.project.seed)
    features = rng.standard_normal((n_steps, n_features)).astype(np.float32)
    labels = np.zeros(n_steps, dtype=np.float32)
    labels[-int(n_steps * 0.15):] = 1.0  # Tipping in final 15% of sequence

    # 4. Temporal Split (no random shuffle to prevent data leakage)
    train_split = int(n_steps * 0.7)
    val_split = int(n_steps * 0.85)

    train_dataset = ClimateTimeSeriesDataset(
        features[:train_split], labels[:train_split], seq_len=cfg.model.architecture.get("max_seq_len", 24)
    )
    val_dataset = ClimateTimeSeriesDataset(
        features[train_split:val_split], labels[train_split:val_split], seq_len=cfg.model.architecture.get("max_seq_len", 24)
    )

    batch_size = cfg.training.batch_size
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    logger.info(f"Temporal Split -> Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

    # 5. Initialize Model Architecture
    model_name = cfg.model.name
    logger.info(f"Instantiating model architecture: {model_name}")
    model = ModelRegistry.create(cfg.model)

    # 6. Initialize Trainer and execute training loop
    trainer = ClimateTrainer(model=model, cfg=cfg.training, full_cfg=cfg)
    history = trainer.fit(train_loader, val_loader)

    # 7. Save final checkpoint and log metrics
    ckpt_path = Path(cfg.paths.checkpoint_dir) / f"{model_name}_{dataset_name}_final.pt"
    trainer.save_checkpoint(ckpt_path)
    
    exp.finish()
    logger.info("Training pipeline completed successfully.")


if __name__ == "__main__":
    main()
