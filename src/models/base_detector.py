from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import numpy as np

class Detection:
    """Represents a single object detection."""
    
    def __init__(
        self,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        class_id: int,
        class_name: str
    ):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bbox": self.bbox,
            "confidence": self.confidence,
            "class_id": self.class_id,
            "class_name": self.class_name
        }

class BaseDetector(ABC):
    """Abstract base class for object detectors."""
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        Detect objects in an image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of Detection objects
        """
        pass
    
    @abstractmethod
    def warmup(self) -> None:
        """Warmup the model (run inference on dummy data)."""
        pass
