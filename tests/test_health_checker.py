import pytest
from unittest.mock import Mock, patch
from src.monitoring.health import HealthChecker, HealthStatus

class TestHealthChecker:
    
    @pytest.fixture
    def mock_redis(self):
        redis = Mock()
        redis.client.ping.return_value = True
        return redis
    
    @pytest.fixture
    def mock_kafka(self):
        kafka = Mock()
        kafka.producer.bootstrap_connected.return_value = True
        return kafka
    
    def test_check_redis_healthy(self, mock_redis):
        """Test Redis health check when healthy."""
        checker = HealthChecker(redis_client=mock_redis)
        result = checker.check_redis()
        
        assert result['status'] == 'healthy'
        assert result['healthy'] is True
    
    def test_check_redis_unhealthy(self, mock_redis):
        """Test Redis health check when unhealthy."""
        mock_redis.client.ping.side_effect = Exception("Connection refused")
        checker = HealthChecker(redis_client=mock_redis)
        result = checker.check_redis()
        
        assert result['status'] == 'unhealthy'
        assert result['healthy'] is False
        assert 'error' in result
    
    def test_check_kafka_healthy(self, mock_kafka):
        """Test Kafka health check when healthy."""
        checker = HealthChecker(kafka_producer=mock_kafka)
        result = checker.check_kafka()
        
        assert result['status'] == 'healthy'
        assert result['healthy'] is True
    
    def test_check_kafka_unhealthy(self, mock_kafka):
        """Test Kafka health check when unhealthy."""
        mock_kafka.producer.bootstrap_connected.return_value = False
        checker = HealthChecker(kafka_producer=mock_kafka)
        result = checker.check_kafka()
        
        assert result['status'] == 'unhealthy'
        assert result['healthy'] is False
    
    def test_check_system_resources(self):
        """Test system resource check."""
        checker = HealthChecker()
        result = checker.check_system_resources()
        
        assert result['status'] == 'healthy'
        assert result['healthy'] is True
        assert 'cpu_percent' in result
        assert 'memory_percent' in result
        assert 'disk_percent' in result
    
    def test_get_health_status_all_healthy(self, mock_redis, mock_kafka):
        """Test overall health status when all components are healthy."""
        checker = HealthChecker(redis_client=mock_redis, kafka_producer=mock_kafka)
        result = checker.get_health_status()
        
        assert result['status'] == HealthStatus.HEALTHY.value
        assert 'components' in result
        assert 'redis' in result['components']
        assert 'kafka' in result['components']
        assert 'system' in result['components']
    
    def test_get_health_status_degraded(self, mock_redis, mock_kafka):
        """Test overall health status when one component is unhealthy."""
        mock_redis.client.ping.side_effect = Exception("Connection failed")
        checker = HealthChecker(redis_client=mock_redis, kafka_producer=mock_kafka)
        result = checker.get_health_status()
        
        assert result['status'] == HealthStatus.DEGRADED.value
