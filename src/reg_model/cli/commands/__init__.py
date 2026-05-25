from .config_cmd import app as config_app
from .data_cmd import app as data_app
# from .evaluate_cmd import app as evaluate_app
# from .feature_cmd import app as feature_app
# from .model_cmd import app as model_app
# from .predict_cmd import app as predict_app
# from .serve_cmd import app as serve_app
# from .train_cmd import app as train_app
from .version_cmd import app as version_app
# from .viz_cmd import app as viz_app

__all__ = [
    'config_app',
    'data_app',
    # 'evaluate_app',
    # 'feature_app',
    # 'model_app',
    # 'predict_app',
    # 'serve_app',
    # 'train_app',
    'version_app',
    # 'viz_app'
]