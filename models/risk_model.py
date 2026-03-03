import tensorflow as tf
from backend.config import settings


def build_risk_model():
    """
    Build a neural network for risk factor-based disease prediction.
    
    Uses patient demographic and health factors to predict respiratory disease risk.
    """
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(32, activation="relu", input_shape=(settings.NUM_RISK_FEATURES,)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(settings.NUM_CLASSES, activation="softmax")
    ], name="RiskFactorModel")
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    return model
