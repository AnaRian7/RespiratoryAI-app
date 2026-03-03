import tensorflow as tf

from backend.config import settings


def build_fusion_model(image_feature_model: tf.keras.Model) -> tf.keras.Model:
    """
    Build a fusion model that combines:
      - Image features from the trained image model
      - Tabular risk factors as a separate input

    The image feature extractor (image_feature_model) is expected to output a
    dense feature vector (e.g., from the penultimate dense layer).
    """
    # Risk-factor input branch
    risk_input = tf.keras.Input(
        shape=(settings.NUM_RISK_FEATURES,),
        name="risk_input",
    )

    x = tf.keras.layers.Dense(16, activation="relu")(risk_input)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)

    # Concatenate image + risk features
    combined = tf.keras.layers.Concatenate()(
        [image_feature_model.output, x]
    )

    out = tf.keras.layers.Dense(
        settings.NUM_CLASSES,
        activation="softmax",
        name="fusion_output",
    )(combined)

    model = tf.keras.Model(
        inputs=[image_feature_model.input, risk_input],
        outputs=out,
        name="FusionModel",
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model
