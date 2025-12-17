from typing import List, Optional
import numpy as np
from mmdet.apis import init_detector, inference_detector
from mmdet.structures import DetDataSample
import torch

from .base_detector import BaseDetector, Detection
from ..config.settings import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__, settings.log_level)

class RTMDetDetector(BaseDetector):
    """RTMDet object detector implementation."""
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        checkpoint_file: Optional[str] = None,
        device: Optional[str] = None,
        score_threshold: Optional[float] = None
    ):
        """
        Initialize RTMDet detector.
        
        Args:
            config_file: Path to model config
            checkpoint_file: Path to model checkpoint
            device: Device to run on ('cuda:0' or 'cpu')
            score_threshold: Confidence threshold for detections
        """
        self.config_file = config_file or settings.detector.config_file
        self.checkpoint_file = checkpoint_file or settings.detector.checkpoint_file
        self.device = device or settings.detector.device
        self.score_threshold = score_threshold or settings.detector.score_threshold
        
        logger.info(f"Initializing RTMDet: {self.config_file}")
        
        try:
            self.model = init_detector(
                self.config_file,
                self.checkpoint_file,
                device=self.device
            )
            logger.info("RTMDet model loaded successfully")
            
            # Warmup
            self.warmup()
            
        except Exception as e:
            logger.error(f"Failed to initialize RTMDet: {e}")
            raise
    
    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        Detect objects in image using RTMDet.
        
        Args:
            image: Input image (BGR format, HWC)
            
        Returns:
            List of Detection objects
        """
        try:
            # Run inference
            result: DetDataSample = inference_detector(self.model, image)
            
            # Extract predictions
            pred_instances = result.pred_instances
            
            detections = []
            for idx in range(len(pred_instances)):
                score = pred_instances.scores[idx].item()
                
                if score < self.score_threshold:
                    continue
                
                bbox = pred_instances.bboxes[idx].cpu().numpy()
                class_id = pred_instances.labels[idx].item()
                class_name = self.model.dataset_meta['classes'][class_id]
                
                detection = Detection(
                    bbox=tuple(bbox),
                    confidence=score,
                    class_id=int(class_id),
                    class_name=class_name
                )
                detections.append(detection)
            
            logger.debug(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def warmup(self, num_iterations: int = 3) -> None:
        """
        Warmup the model with dummy data.
        
        Args:
            num_iterations: Number of warmup iterations
        """
        logger.info("Warming up RTMDet model...")
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        
        for i in range(num_iterations):
            self.detect(dummy_image)
        
        logger.info("RTMDet warmup complete")
