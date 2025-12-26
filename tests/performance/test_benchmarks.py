import pytest
import time
import numpy as np
from unittest.mock import MagicMock, patch

class TestPerformanceBenchmarks:
    """Benchmarks to ensure system meets core latency requirements."""
    
    @pytest.mark.benchmark
    def test_pydantic_serialization_speed(self):
        """Ensure event serialization is sub-millisecond."""
        from src.events.event_schemas import MotionDetectionEvent, EventType
        from datetime import datetime
        
        start_time = time.perf_counter()
        
        for _ in range(1000):
            event = MotionDetectionEvent(
                event_id="test",
                camera_id="cam1",
                frame_number=1,
                detected_objects=[{"class": "person"}],
                total_objects=1,
                confidence_scores=[0.9]
            )
            _ = event.model_dump_json()
            
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 1000
        
        print(f"\nAverage serialization time: {avg_time*1000:.4f}ms")
        assert avg_time < 0.001  # Should be < 1ms
    
    def test_logger_overhead(self):
        """Ensure logging doesn't slow down the main loop significantly."""
        from src.utils.logger import setup_logger
        import logging
        
        logger = setup_logger("bench", "INFO")
        # Direct to devnull or mock to avoid terminal IO bottleneck
        for handler in logger.handlers:
            handler.setLevel(logging.CRITICAL)
            
        start_time = time.perf_counter()
        for i in range(1000):
            logger.info(f"Benchmark log entry {i}")
        end_time = time.perf_counter()
        
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.0005  # Should be < 0.5ms
