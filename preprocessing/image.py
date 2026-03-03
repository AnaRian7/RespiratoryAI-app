import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from backend.config import settings


def get_image_generators(return_df=False):
    conn = sqlite3.connect(settings.DB_PATH)

    df = pd.read_sql(
        "SELECT filepath, label FROM xray_images",
        conn
    )
    conn.close()

    train_df, val_df = train_test_split(
        df,
        test_size=settings.VALIDATION_SPLIT,
        stratify=df["label"],
        random_state=42
    )

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=15,
        zoom_range=0.1,
        horizontal_flip=True
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_gen = train_datagen.flow_from_dataframe(
        train_df,
        x_col="filepath",
        y_col="label",
        target_size=settings.IMAGE_SIZE,
        class_mode="categorical",   # ✅ ONE-HOT
        batch_size=settings.BATCH_SIZE,
        shuffle=True
    )

    val_gen = val_datagen.flow_from_dataframe(
        val_df,
        x_col="filepath",
        y_col="label",
        target_size=settings.IMAGE_SIZE,
        class_mode="categorical",   # ✅ ONE-HOT
        batch_size=settings.BATCH_SIZE,
        shuffle=False
    )

    if return_df:
        return train_gen, val_gen, df

    return train_gen, val_gen
