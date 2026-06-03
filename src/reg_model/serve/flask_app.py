#!/usr/bin/env python
# Copyright (c) 2026--2030. Wang Weihua
# All rights reserved.
"""Flask prediction API application module."""

import os
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request  # type: ignore  # optional dep


def create_app(model_path: str | None = None) -> Flask:
    """Create and configure the Flask prediction API app.

    Args:
        model_path: Path to the model file. If None, reads from MODEL_PATH env var.

    Returns:
        Configured Flask application
    """
    if model_path is None:
        model_path = os.environ.get('MODEL_PATH', '')
    if not model_path:
        raise ValueError('MODEL_PATH is required')

    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f'Model file not found: {model_file}')

    bundle = joblib.load(model_file)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_names = bundle['feature_names']

    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'model': str(model_file)})

    @app.route('/predict', methods=['POST'])
    def predict():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Request body must be JSON'}), 400

            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return jsonify({'error': 'Invalid data format'}), 400

            missing = set(feature_names) - set(df.columns)
            if missing:
                return jsonify({'error': f'Missing features: {missing}'}), 400

            features = df[feature_names]
            features_scaled = scaler.transform(features)
            predictions = model.predict(features_scaled).tolist()

            return jsonify({'predictions': predictions})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/info', methods=['GET'])
    def info():
        return jsonify(
            {
                'algorithm': bundle.get('algorithm', 'unknown'),
                'feature_names': feature_names,
                'feature_count': len(feature_names),
            }
        )

    return app
