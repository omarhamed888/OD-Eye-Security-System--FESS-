import pytest
from unittest.mock import Mock, patch, MagicMock
from src.events.kafka_producer import KafkaEventProducer

class TestKafkaProducer:
    
    @pytest.fixture
    def mock_kafka_producer(self):
        with patch('src.events.kafka_producer.KafkaProducer') as mock:
            yield mock
    
    def test_send_event_success(self, mock_kafka_producer):
        """Test successful event sending."""
        producer = KafkaEventProducer()
        
        # Mock successful send
        future = Mock()
        future.get.return_value = Mock(partition=0, offset=123)
        producer.producer.send.return_value = future
        
        event = {"test": "data"}
        result = producer.send_event("test_topic", event)
        
        assert result is True
        producer.producer.send.assert_called_once()
    
    def test_send_event_failure(self, mock_kafka_producer):
        """Test event sending failure."""
        from kafka.errors import KafkaError
        
        producer = KafkaEventProducer()
        
        # Mock failed send
        future = Mock()
        future.get.side_effect = KafkaError("Connection failed")
        producer.producer.send.return_value = future
        
        event = {"test": "data"}
        result = producer.send_event("test_topic", event)
        
        assert result is False
    
    def test_close_producer(self, mock_kafka_producer):
        """Test producer close."""
        producer = KafkaEventProducer()
        producer.close()
        
        producer.producer.close.assert_called_once()
