import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.layers import (
    Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)

from backend.preprocessing.image import get_image_generators
from backend.config import settings


def build_image_model(freeze_base: bool = True):
    """
    Build ResNet50V2-based image classification model for chest X-rays.
    
    Args:
        freeze_base: If True, freeze early layers for transfer learning.
    
    Returns:
        Compiled Keras model.
    """
    base = ResNet50V2(
        weights="imagenet",
        include_top=False,
        input_shape=(*settings.IMAGE_SIZE, 3)
    )

    if freeze_base:
        for layer in base.layers[:-30]:
            layer.trainable = False
        for layer in base.layers[-30:]:
            layer.trainable = True
    else:
        base.trainable = True

    x = GlobalAveragePooling2D(name="global_pool")(base.output)
    x = BatchNormalization(name="bn_1")(x)
    x = Dropout(0.5, name="dropout_1")(x)
    x = Dense(256, activation="relu", name="dense_256")(x)
    x = BatchNormalization(name="bn_2")(x)
    x = Dropout(0.3, name="dropout_2")(x)

    output = Dense(
        settings.NUM_CLASSES,
        activation="softmax",
        name="predictions"
    )(x)

    model = Model(inputs=base.input, outputs=output, name="ResNet50V2_ChestXray")

    model.compile(
        optimizer=Adam(learning_rate=settings.LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc", multi_label=False)
        ]
    )

    return model


def get_callbacks():
    """Get training callbacks for early stopping, LR scheduling, and checkpointing."""
    return [
        EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=settings.IMAGE_MODEL_PATH,
            monitor="val_auc",
            mode="max",
            save_best_only=True,
            verbose=1
        )
    ]


def train_image_model(fine_tune: bool = False):
    """
    Train the ResNet50V2 image model on chest X-ray data.
    
    Args:
        fine_tune: If True, unfreeze more layers for fine-tuning (use after initial training).
    
    Returns:
        Training history and evaluation metrics.
    """
    train_gen, val_gen, df = get_image_generators(return_df=True)

    print("\n" + "="*60)
    print("CHEST X-RAY CLASSIFICATION - TRAINING")
    print("="*60)
    print(f"\nModel: ResNet50V2")
    print(f"Image size: {settings.IMAGE_SIZE}")
    print(f"Classes: {settings.CLASSES}")
    print(f"Epochs: {settings.EPOCHS}")
    print(f"Batch size: {settings.BATCH_SIZE}")
    print(f"Learning rate: {settings.LEARNING_RATE}")

    print("\n📊 Class distribution:")
    print(df["label"].value_counts())
    print(f"\nTotal samples: {len(df)}")
    print(f"Training samples: {len(train_gen.filenames)}")
    print(f"Validation samples: {len(val_gen.filenames)}")

    class_indices = train_gen.class_indices
    df["label_idx"] = df["label"].map(class_indices)

    class_weights_array = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(df["label_idx"]),
        y=df["label_idx"]
    )

    class_weights = dict(
        zip(np.unique(df["label_idx"]), class_weights_array)
    )

    print("\n⚖️ Class weights (handling imbalance):")
    for cls, weight in class_weights.items():
        class_name = [k for k, v in class_indices.items() if v == cls][0]
        print(f"  {class_name}: {weight:.3f}")

    model = build_image_model(freeze_base=not fine_tune)

    print(f"\nModel parameters: {model.count_params():,}")
    trainable = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    print(f"Trainable parameters: {trainable:,}")

    print("\n🚀 Starting training...\n")

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=settings.EPOCHS,
        class_weight=class_weights,
        callbacks=get_callbacks(),
        verbose=1
    )

    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)

    val_results = model.evaluate(val_gen, verbose=0)
    metrics_names = model.metrics_names

    for name, value in zip(metrics_names, val_results):
        print(f"  {name}: {value:.4f}")

    model.save(settings.IMAGE_MODEL_PATH)
    print(f"\n✅ Model saved: {settings.IMAGE_MODEL_PATH}")

    return history, dict(zip(metrics_names, val_results))
