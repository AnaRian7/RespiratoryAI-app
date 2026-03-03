"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for model explainability.

Generates heatmaps showing which regions of the X-ray image
most influenced the model's prediction.

Reference: https://arxiv.org/abs/1610.02391
"""

import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image
import io
import base64

from backend.config import settings


class GradCAM:
    """Generate Grad-CAM visualizations for ResNet50V2 predictions."""
    
    def __init__(self, model: tf.keras.Model, layer_name: str = None):
        """
        Initialize Grad-CAM generator.
        
        Args:
            model: Trained Keras model
            layer_name: Target convolutional layer for Grad-CAM.
                        If None, uses last conv layer before global pooling.
        """
        self.model = model
        self.layer_name = layer_name or self._find_target_layer()
        
        self.grad_model = tf.keras.Model(
            inputs=self.model.input,
            outputs=[
                self.model.get_layer(self.layer_name).output,
                self.model.output
            ]
        )
    
    def _find_target_layer(self) -> str:
        """Find the last convolutional layer in the model."""
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                return layer.name
            if hasattr(layer, 'layers'):
                for sublayer in reversed(layer.layers):
                    if isinstance(sublayer, tf.keras.layers.Conv2D):
                        return sublayer.name
        
        for layer in self.model.layers:
            if 'conv' in layer.name.lower():
                return layer.name
        
        raise ValueError("Could not find a convolutional layer for Grad-CAM")
    
    def compute_heatmap(
        self,
        image: np.ndarray,
        class_idx: int = None,
        eps: float = 1e-8
    ) -> np.ndarray:
        """
        Compute Grad-CAM heatmap for an image.
        
        Args:
            image: Preprocessed image array of shape (1, H, W, 3)
            class_idx: Target class index. If None, uses predicted class.
            eps: Small value to avoid division by zero
            
        Returns:
            Heatmap as numpy array of shape (H, W) with values in [0, 1]
        """
        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.grad_model(image)
            
            if class_idx is None:
                class_idx = tf.argmax(predictions[0])
            
            class_output = predictions[:, class_idx]
        
        grads = tape.gradient(class_output, conv_outputs)
        
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)
        
        heatmap = tf.nn.relu(heatmap)
        heatmap = heatmap / (tf.reduce_max(heatmap) + eps)
        
        return heatmap.numpy()
    
    def overlay_heatmap(
        self,
        heatmap: np.ndarray,
        original_image: np.ndarray | Image.Image,
        alpha: float = 0.4,
        colormap: str = "jet"
    ) -> Image.Image:
        """
        Overlay Grad-CAM heatmap on original image.
        
        Args:
            heatmap: Grad-CAM heatmap of shape (H, W)
            original_image: Original image (PIL Image or numpy array)
            alpha: Transparency for heatmap overlay
            colormap: Matplotlib colormap name
            
        Returns:
            PIL Image with heatmap overlay
        """
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        
        if isinstance(original_image, np.ndarray):
            if original_image.max() <= 1.0:
                original_image = (original_image * 255).astype(np.uint8)
            original_image = Image.fromarray(original_image)
        
        original_size = original_image.size
        
        heatmap_resized = np.array(
            Image.fromarray((heatmap * 255).astype(np.uint8)).resize(
                original_size, Image.Resampling.BILINEAR
            )
        ) / 255.0
        
        cmap = cm.get_cmap(colormap)
        heatmap_colored = cmap(heatmap_resized)[:, :, :3]
        heatmap_colored = (heatmap_colored * 255).astype(np.uint8)
        heatmap_image = Image.fromarray(heatmap_colored)
        
        original_rgb = original_image.convert("RGB")
        overlaid = Image.blend(original_rgb, heatmap_image, alpha=alpha)
        
        return overlaid
    
    def generate_visualization(
        self,
        image_path: str | Path,
        class_idx: int = None,
        save_path: str | Path = None,
        return_base64: bool = False
    ) -> dict:
        """
        Generate complete Grad-CAM visualization for an image file.
        
        Args:
            image_path: Path to input X-ray image
            class_idx: Target class index (None = use prediction)
            save_path: Optional path to save the visualization
            return_base64: If True, include base64-encoded image in result
            
        Returns:
            Dictionary with prediction info and optional visualization data
        """
        original_image = Image.open(image_path).convert("RGB")
        
        img_array = original_image.resize(settings.IMAGE_SIZE)
        img_array = np.array(img_array) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = self.model.predict(img_array, verbose=0)[0]
        predicted_class_idx = int(np.argmax(predictions))
        predicted_class = settings.INDEX_TO_CLASS[predicted_class_idx]
        confidence = float(predictions[predicted_class_idx])
        
        target_class = class_idx if class_idx is not None else predicted_class_idx
        
        heatmap = self.compute_heatmap(img_array, class_idx=target_class)
        
        overlaid_image = self.overlay_heatmap(heatmap, original_image)
        
        result = {
            "predicted_class": predicted_class,
            "predicted_class_idx": predicted_class_idx,
            "confidence": confidence,
            "probabilities": {
                settings.INDEX_TO_CLASS[i]: float(p)
                for i, p in enumerate(predictions)
            },
            "target_class_idx": target_class,
            "target_class": settings.INDEX_TO_CLASS[target_class],
        }
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            overlaid_image.save(save_path)
            result["gradcam_path"] = str(save_path)
        
        if return_base64:
            buffer = io.BytesIO()
            overlaid_image.save(buffer, format="PNG")
            buffer.seek(0)
            result["gradcam_base64"] = base64.b64encode(buffer.read()).decode("utf-8")
        
        return result, overlaid_image


def create_gradcam(model: tf.keras.Model) -> GradCAM:
    """Factory function to create GradCAM instance."""
    return GradCAM(model)
