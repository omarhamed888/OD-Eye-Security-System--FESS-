import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.models.rtmdet_detector import RTMDetDetector
from src.events.event_publisher import EventPublisher
from src.cache.face_cache import FaceCache

class TestEndToEndFlow:
    """Simulation of the full detection → cache → event flow."""
    
    @patch('src.events.event_publisher.KafkaEventProducer')
    @patch('src.cache.face_cache.RedisCache')
    @patch('src.models.rtmdet_detector.init_detector')
    @patch('src.models.rtmdet_detector.inference_detector')
    def test_detection_to_event_pipeline(self, 
                                        mock_inference, 
                                        mock_init, 
                                        mock_redis, 
                                        mock_kafka):
        """
        Tests that a frame processing leads to cache interaction 
        and event publishing.
        """
        # 1. Setup Detector Mock
        mock_model = MagicMock()
        mock_model.dataset_meta = {'classes': ('person', 'bicycle', 'car')}
        mock_init.return_value = mock_model
        
        # Define real numpy arrays for simulation
        scores_arr = np.array([0.95], dtype=np.float32)
        bboxes_arr = np.array([[10, 10, 50, 50]], dtype=np.float32)
        labels_arr = np.array([0], dtype=np.int64)

        # Mock the result structure to match MMDetection 3.x
        mock_result = MagicMock()
        mock_instances = MagicMock()
        
        # Helper to simulate PyTorch tensor .item() and indexing
        def mock_tensor(arr):
            m = MagicMock()
            m.__getitem__.side_effect = lambda idx: MagicMock(
                item=MagicMock(return_value=arr[idx]),
                cpu=MagicMock(return_value=MagicMock(
                    numpy=MagicMock(return_value=arr[idx])
                ))
            )
            m.__len__.return_value = len(arr)
            m.cpu.return_value.numpy.return_value = arr
            return m

        mock_instances.bboxes = mock_tensor(bboxes_arr)
        mock_instances.scores = mock_tensor(scores_arr)
        mock_instances.labels = mock_tensor(labels_arr)
        mock_instances.__len__.return_value = 1
        
        mock_result.pred_instances = mock_instances
        mock_inference.return_value = mock_result
        
        # 2. Setup Detector and Publisher
        detector = RTMDetDetector()
        mock_prod = mock_kafka.return_value
        mock_prod.send_event.return_value = True
        publisher = EventPublisher(kafka_producer=mock_prod)
        
        # 3. Process Frame
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        detections = detector.detect(frame)
        
        # 4. Verify Detection Result
        assert len(detections) == 1
        assert detections[0].class_name == "person"
        
        # 5. Verify Event Publishing
        result = publisher.publish_motion_event(
            camera_id="cam_01",
            frame_number=1,
            detected_objects=[d.__dict__ for d in detections],
            confidence_scores=[d.confidence for d in detections]
        )
        
        assert result is True
        mock_prod.send_event.assert_called_once()
        
    def test_system_health_aggregation(self, mock_redis, mock_kafka):
        """Test health checker aggregates correctly from mocks."""
        from src.monitoring.health import HealthChecker
        
        checker = HealthChecker(
            redis_client=mock_redis,
            kafka_producer=mock_kafka
        )
        
        status = checker.get_health_status()
        assert status['status'] == "healthy"
        assert status['components']['redis']['healthy'] is True
        assert status['components']['kafka']['healthy'] is True
