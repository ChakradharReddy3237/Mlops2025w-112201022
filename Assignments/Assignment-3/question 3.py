# ==============================================================================
# question3.py - Full Solution for Assignment 3, Question 3
#
# This script designs and executes a machine learning pipeline as specified.
# It integrates configurations from JSON and TOML, runs model inference,
# and simulates a hyperparameter grid search.
#
# To run this script, ensure you have the necessary libraries installed:
# pip install torch torchvision toml
# ==============================================================================

import json
import toml
import torch
import torchvision.models as models
from itertools import product
from typing import Dict, List, Any, Generator

# ==============================================================================
# PART B & C: Define Configurations
# In a real-world scenario, these would be in separate files (e.g., config.json).
# For this single-file submission, they are defined as multi-line strings.
# ==============================================================================

# --- b. Specify data source and model architecture using JSON ---
JSON_PIPELINE_CONFIG = """
{
  "project_name": "ImageClassificationPipeline",
  "data_source": {
    "type": "ImageFolder",
    "train_path": "/path/to/imagenet/train",
    "validation_path": "/path/to/imagenet/val"
  },
  "architectures": ["resnet34", "resnet50", "resnet101", "resnet152"]
}
"""

# --- c. Define model parameters for each architecture using TOML ---
TOML_MODEL_PARAMS_CONFIG = """
# Default parameters for different ResNet architectures
# These would be the starting point before hyperparameter tuning.

[[models]]
name = "resnet34"
learning_rate = 0.001
batch_size = 64
optimizer = "Adam"
scheduler = "StepLR"

[[models]]
name = "resnet50"
learning_rate = 0.001
batch_size = 32
optimizer = "Adam"
scheduler = "StepLR"

[[models]]
name = "resnet101"
learning_rate = 0.0005
batch_size = 32
optimizer = "SGD"
scheduler = "CosineAnnealingLR"
momentum = 0.9

[[models]]
name = "resnet152"
learning_rate = 0.0005
batch_size = 16
optimizer = "SGD"
scheduler = "CosineAnnealingLR"
momentum = 0.9
"""

# --- e. Define hyperparameter search space using JSON ---
JSON_GRID_SEARCH_CONFIG = """
{
    "description": "Grid search for hyperparameter optimization.",
    "target_metric": "validation_accuracy",
    "grid_search_params": {
        "learning_rate": [0.1, 0.01, 0.001],
        "optimizer": ["adam", "sgd"],
        "momentum": [0.5, 0.9]
    }
}
"""


class MLPipeline:
    """
    An object-oriented implementation of the ML pipeline.
    This class loads configurations, runs inference on specified models,
    and orchestrates a hyperparameter tuning process.
    """

    def __init__(self, pipeline_config_str: str, model_params_str: str, grid_search_config_str: str):
        """
        Initializes the pipeline by loading all necessary configurations.
        """
        print("Initializing ML Pipeline...")
        self.pipeline_config = self._load_json(pipeline_config_str)
        model_params_list = self._load_toml(model_params_str)['models']
        self.grid_search_config = self._load_json(grid_search_config_str)

        # Convert the list of model parameters from TOML into a dictionary for easy lookup
        self.model_params = {model['name']: model for model in model_params_list}
        print("Configurations loaded successfully.")

    def _load_json(self, config_str: str) -> Dict[str, Any]:
        """Safely loads a JSON configuration from a string."""
        return json.loads(config_str)

    def _load_toml(self, config_str: str) -> Dict[str, Any]:
        """Safely loads a TOML configuration from a string."""
        return toml.loads(config_str)

    def run_inference_for_all_architectures(self):
        """
        Part (d) - Integration and Inference:
        Iterates through the architectures defined in the JSON config,
        retrieves their parameters from the TOML config, and runs inference.
        """
        print("\n" + "="*80)
        print("PART D: RUNNING INFERENCE PIPELINE FOR PRE-CONFIGURED MODELS")
        print("="*80)
        
        architectures = self.pipeline_config.get("architectures", [])
        if not architectures:
            print("No architectures found in pipeline configuration.")
            return

        for arch_name in architectures:
            if arch_name in self.model_params:
                params = self.model_params[arch_name]
                print(f"\n>>> Processing Architecture: {arch_name}")
                print(f"    - Base Parameters (from TOML):")
                for key, value in params.items():
                    if key != 'name':
                        print(f"      - {key}: {value}")
                
                # Part (a): Call the inference function for this model
                self._perform_inference(arch_name)
            else:
                print(f"\n[WARNING] Parameters for architecture '{arch_name}' not found in TOML config.")
    
    @staticmethod
    def _perform_inference(model_name: str):
        """
        Part (a) - Model Inference:
        Loads a pre-trained ResNet model from torchvision, creates a dummy input,
        and performs a forward pass to demonstrate inference.
        """
        print(f"--- Running Inference for: {model_name} ---")
        try:
            # Dynamically get the model constructor from torchvision.models
            model_constructor = getattr(models, model_name)
            
            print(f"    - Loading pre-trained '{model_name}' weights (ImageNet)...")
            model = model_constructor(weights='IMAGENET1K_V1')
            model.eval()  # Set the model to evaluation mode
            
            # Create a dummy input tensor representing a single 224x224 RGB image
            dummy_input = torch.randn(1, 3, 224, 224)
            
            print(f"    - Performing inference on a dummy input tensor of shape {dummy_input.shape}...")
            with torch.no_grad():
                output = model(dummy_input)
            
            print(f"    - SUCCESS: Inference complete. Output tensor shape: {output.shape}")
        except AttributeError:
            print(f"    - ERROR: Model '{model_name}' not found in torchvision.models.")
        except Exception as e:
            print(f"    - ERROR: An error occurred during inference for {model_name}: {e}")

    def run_hyperparameter_tuning(self):
        """
        Part (e) - Hyperparameter Tuning:
        Constructs and executes a grid search based on the parameters
        defined in the grid search JSON configuration.
        """
        print("\n" + "="*80)
        print("PART E: HYPERPARAMETER TUNING (GRID SEARCH SIMULATION)")
        print("="*80)

        params_to_tune = self.grid_search_config.get("grid_search_params", {})
        if not params_to_tune:
            print("No grid search parameters found in configuration.")
            return

        # Create a list of all hyperparameter combinations (the "grid")
        param_names = list(params_to_tune.keys())
        param_values = list(params_to_tune.values())
        grid = list(product(*param_values))

        print(f"Target metric: '{self.grid_search_config.get('target_metric')}'")
        print(f"Total combinations to test: {len(grid)}")
        print("Simulating training and evaluation for each combination on a sample model (e.g., resnet18)...")

        best_score = -1.0
        best_params = {}

        for i, combination in enumerate(grid):
            # Create a dictionary for the current set of parameters
            current_params = dict(zip(param_names, combination))

            # --- Optimization: Skip irrelevant combinations ---
            # The 'momentum' parameter is only used by the 'sgd' optimizer.
            # This check avoids redundant runs for 'adam'.
            if current_params.get('optimizer') != 'sgd' and 'momentum' in current_params:
                # If this is not the first momentum value, skip, as it's a repeat for this optimizer
                if current_params['momentum'] != params_to_tune['momentum'][0]:
                    continue

            print(f"\n--- Run {i+1}/{len(grid)} ---")
            
            # Simulate a training run with these parameters
            # In a real scenario, this function would train the model and return a validation score.
            simulated_score = self._simulate_training_run(current_params)

            if simulated_score > best_score:
                best_score = simulated_score
                best_params = current_params
        
        print("\n" + "-"*80)
        print("Grid Search Simulation Complete.")
        print(f"Best Simulated Score ({self.grid_search_config.get('target_metric')}): {best_score:.4f}")
        print("Best Hyperparameters Found:")
        for key, value in best_params.items():
            print(f"  - {key}: {value}")
        print("-" * 80)
    
    @staticmethod
    def _simulate_training_run(params: Dict[str, Any]) -> float:
        """
        A placeholder function that simulates a full model training and evaluation.
        In a real pipeline, this would involve:
        1. Creating a DataLoader for the training data.
        2. Initializing the model, optimizer, and learning rate scheduler.
        3. Running the training loop for a set number of epochs.
        4. Evaluating the model on a validation set.
        5. Returning the final score on the target metric.
        """
        print("  - Parameters:")
        for key, value in params.items():
            print(f"    - {key}: {value}")
        print("  - [SIMULATION] Initializing model and DataLoader...")
        print("  - [SIMULATION] Training for 10 epochs...")
        print("  - [SIMULATION] Evaluating on validation set...")
        
        # Generate a fake score to make the simulation dynamic.
        # A simple hash gives a deterministic but "random-looking" score.
        score = (hash(tuple(sorted(params.items()))) % 1000) / 1000.0 + 0.9
        print(f"  - [SIMULATION] Result: Validation Accuracy = {score:.4f}")
        return score


def main():
    """
    Main execution function to run the entire pipeline.
    """
    print("=========================================")
    print("   ML Pipeline Design and Execution      ")
    print("=========================================")
    try:
        # Instantiate the pipeline with the string-based configurations
        pipeline = MLPipeline(
            pipeline_config_str=JSON_PIPELINE_CONFIG,
            model_params_str=TOML_MODEL_PARAMS_CONFIG,
            grid_search_config_str=JSON_GRID_SEARCH_CONFIG
        )
        
        # Execute the pipeline steps
        pipeline.run_inference_for_all_architectures()
        pipeline.run_hyperparameter_tuning()
        
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
        print("Pipeline execution halted.")

if __name__ == "__main__":
    main()