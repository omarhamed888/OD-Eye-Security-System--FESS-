from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, List
import os

class RedisSettings(BaseSettings):
    host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    port: int = Field(default=6379, validation_alias="REDIS_PORT")
    db: int = Field(default=0, validation_alias="REDIS_DB")
    password: Optional[str] = Field(default=None, validation_alias="REDIS_PASSWORD")
    max_connections: int = Field(default=50, validation_alias="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=5, validation_alias="REDIS_SOCKET_TIMEOUT")
    
    model_config = SettingsConfigDict(env_ignore_empty=True, extra='ignore')

class DetectorSettings(BaseSettings):
    model_name: str = Field(default="rtmdet-tiny", validation_alias="DETECTOR_MODEL")
    config_file: str = Field(default="configs/rtmdet_tiny_8xb32-300e_coco.py")
    checkpoint_file: str = Field(default="checkpoints/rtmdet_tiny_8xb32-300e_coco.pth")
    device: str = Field(default="cuda:0", validation_alias="DETECTOR_DEVICE")
    score_threshold: float = Field(default=0.5, validation_alias="DETECTOR_SCORE_THRESHOLD")
    nms_threshold: float = Field(default=0.45, validation_alias="DETECTOR_NMS_THRESHOLD")
    
    @field_validator('score_threshold', 'nms_threshold')
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        return v
        
    model_config = SettingsConfigDict(env_ignore_empty=True, extra='ignore')

class CacheSettings(BaseSettings):
    face_ttl: int = Field(default=3600, validation_alias="CACHE_FACE_TTL")  # 1 hour
    detection_ttl: int = Field(default=300, validation_alias="CACHE_DETECTION_TTL")  # 5 min
    max_face_encodings: int = Field(default=10000, validation_alias="CACHE_MAX_FACES")
    
    model_config = SettingsConfigDict(env_ignore_empty=True, extra='ignore')
    
class KafkaSettings(BaseSettings):
    bootstrap_servers: List[str] = Field(default=["localhost:9092"])
    topic_motion_events: str = Field(default="motion.detection.events", validation_alias="KAFKA_TOPIC_MOTION")
    topic_face_events: str = Field(default="face.recognition.events", validation_alias="KAFKA_TOPIC_FACES")
    topic_alert_events: str = Field(default="alert.events", validation_alias="KAFKA_TOPIC_ALERTS")
    
    # Producer settings
    acks: str = Field(default="1", validation_alias="KAFKA_ACKS")
    compression_type: str = Field(default="snappy", validation_alias="KAFKA_COMPRESSION")
    linger_ms: int = Field(default=10, validation_alias="KAFKA_LINGER_MS")
    batch_size: int = Field(default=16384, validation_alias="KAFKA_BATCH_SIZE")
    max_request_size: int = Field(default=1048576, validation_alias="KAFKA_MAX_REQUEST_SIZE")
    
    # Security (optional)
    security_protocol: str = Field(default="PLAINTEXT", validation_alias="KAFKA_SECURITY_PROTOCOL")
    sasl_mechanism: Optional[str] = Field(default=None, validation_alias="KAFKA_SASL_MECHANISM")
    sasl_username: Optional[str] = Field(default=None, validation_alias="KAFKA_SASL_USERNAME")
    sasl_password: Optional[str] = Field(default=None, validation_alias="KAFKA_SASL_PASSWORD")
    
    model_config = SettingsConfigDict(env_ignore_empty=True, extra='ignore')

class Settings(BaseSettings):
    redis: RedisSettings = Field(default_factory=RedisSettings)
    detector: DetectorSettings = Field(default_factory=DetectorSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore',
        env_nested_delimiter='__'
    )

# Singleton instance
settings = Settings()
