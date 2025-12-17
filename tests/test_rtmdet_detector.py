import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import torch  # Required for the mock tensors

from src.models.rtmdet_detector import RTMDetDetector
from src.models.base_detector import Detection

class TestRTMDetDetector:
    
    @pytest.fixture
    def mock_model(self):
        """Mock MMDetection model."""
        model = Mock()
        model.dataset_meta = {
            'classes': ['person', 'car', 'bicycle']
        }
        return model
    
    @pytest.fixture
    def detector(self, mock_model):
        """Create detector with mocked model."""
        with patch('src.models.rtmdet_detector.init_detector', return_value=mock_model):
            # We also need to mock warmup since it calls detect which uses inference_detector
            # But the detector's model is not set until init_detector returns.
            # Actually, init_detector returns the model, then we assign it. 
            # Then warmup calls detect(dummy_image). detect calls inference_detector.
            # So if we mock init_detector, we get mock_model.
            # Then warmup runs. detect runs. inference_detector is global.
            # We need to mock inference_detector during init too because warmup calls it.
            
            with patch('src.models.rtmdet_detector.inference_detector') as mock_inference:
                # Setup mock inference return for warmup
                warmup_result = Mock()
                warmup_instances = MagicMock()
                warmup_instances.__len__.return_value = 0
                warmup_instances.scores = torch.tensor([]) 
                warmup_instances.bboxes = torch.tensor([])
                warmup_instances.labels = torch.tensor([])
                warmup_result.pred_instances = warmup_instances
                mock_inference.return_value = warmup_result
                
                detector = RTMDetDetector()
                detector.model = mock_model
                return detector
    
    def test_detect_success(self, detector):
        """Test successful detection."""
        # Mock inference result
        mock_result = Mock()
        mock_instances = MagicMock()
        mock_instances.__len__.return_value = 2
        # Use simple tensors for mocking
        mock_instances.scores = torch.tensor([0.9, 0.8])
        mock_instances.bboxes = torch.tensor([
            [100, 100, 200, 200],
            [300, 300, 400, 400]
        ])
        mock_instances.labels = torch.tensor([0, 1])
        mock_result.pred_instances = mock_instances
        
        with patch('src.models.rtmdet_detector.inference_detector', return_value=mock_result):
            image = np.zeros((640, 640, 3), dtype=np.uint8)
            detections = detector.detect(image)
        
        assert len(detections) == 2
        assert all(isinstance(d, Detection) for d in detections)
        assert detections[0].class_name == 'person'
        assert detections[1].class_name == 'car'
    
    def test_detect_filters_low_confidence(self, detector):
        """Test that low confidence detections are filtered."""
        # Set high threshold
        detector.score_threshold = 0.9
        
        # Mock result with mixed confidences
        mock_result = Mock()
        mock_instances = MagicMock()
        mock_instances.__len__.return_value = 2
        mock_instances.scores = torch.tensor([0.95, 0.5])
        mock_instances.bboxes = torch.tensor([
            [100, 100, 200, 200],
            [300, 300, 400, 400]
        ])
        mock_instances.labels = torch.tensor([0, 0])
        mock_result.pred_instances = mock_instances
        
        with patch('src.models.rtmdet_detector.inference_detector', return_value=mock_result):
            image = np.zeros((640, 640, 3), dtype=np.uint8)
            detections = detector.detect(image)
        
        # Only high confidence detection should remain
        assert len(detections) == 1
        assert detections[0].confidence == pytest.approx(0.95)
