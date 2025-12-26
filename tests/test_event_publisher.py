import pytest
from unittest.mock import Mock, patch
from src.events.event_publisher import EventPublisher
from src.events.event_schemas import EventType

class TestEventPublisher:
    
    @pytest.fixture
    def mock_kafka(self):
        with patch('src.events.event_publisher.KafkaEventProducer') as mock:
            kafka_instance = Mock()
            kafka_instance.send_event.return_value = True
            mock.return_value = kafka_instance
            yield kafka_instance
    
    def test_publish_motion_event(self, mock_kafka):
        """Test publishing motion detection event."""
        publisher = EventPublisher(kafka_producer=mock_kafka)
        
        result = publisher.publish_motion_event(
            camera_id="cam_01",
            frame_number=100,
            detected_objects=[{"class": "person", "bbox": [0, 0, 100, 100]}],
            confidence_scores=[0.95]
        )
        
        assert result is True
        mock_kafka.send_event.assert_called_once()
        
        # Verify event structure
        call_args = mock_kafka.send_event.call_args
        assert call_args[1]['key'] == "cam_01"
        event_data = call_args[1]['event']
        assert event_data['camera_id'] == "cam_01"
        assert event_data['frame_number'] == 100
        assert event_data['total_objects'] == 1
    
    def test_publish_face_event(self, mock_kafka):
        """Test publishing face recognition event."""
        publisher = EventPublisher(kafka_producer=mock_kafka)
        
        result = publisher.publish_face_event(
            camera_id="cam_01",
            frame_number=150,
            face_id="face_123",
            bbox=(10, 20, 30, 40),
            confidence=0.98,
            person_name="John Doe",
            is_authorized=True
        )
        
        assert result is True
        mock_kafka.send_event.assert_called_once()
        
        # Verify event structure
        call_args = mock_kafka.send_event.call_args
        event_data = call_args[1]['event']
        assert event_data['face_id'] == "face_123"
        assert event_data['person_name'] == "John Doe"
        assert event_data['is_authorized'] is True
    
    def test_publish_alert(self, mock_kafka):
        """Test publishing alert event."""
        publisher = EventPublisher(kafka_producer=mock_kafka)
        
        result = publisher.publish_alert(
            camera_id="cam_01",
            alert_level="CRITICAL",
            message="Unauthorized access detected",
            associated_event_ids=["event_1", "event_2"]
        )
        
        assert result is True
        mock_kafka.send_event.assert_called_once()
        
        # Verify event structure
        call_args = mock_kafka.send_event.call_args
        event_data = call_args[1]['event']
        assert event_data['alert_level'] == "CRITICAL"
        assert event_data['alert_message'] == "Unauthorized access detected"
        assert len(event_data['associated_events']) == 2
