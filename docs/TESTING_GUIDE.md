# FESS Testing Suite Guide

## 🧪 Running Tests

### 1. Run All Tests
```bash
python -m pytest
```

### 2. Run Specific Categories
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Performance benchmarks
python -m pytest tests/performance/
```

### 3. Coverage Reports
The system is configured to fail if coverage falls below **85%**.
- After running tests, open `htmlcov/index.html` to see the detailed report.

## 🛠️ Test Structure

1. **Unit Tests**: Test logic in isolation using mocks for Redis/Kafka.
2. **Integration Tests**: Verify that Detector, Cache, and Events work together.
3. **E2E Simulations**: Full flow from "frame ingress" to "event published".
4. **Benchmarks**: Measure latency of core operations.

## 🚀 CI/CD
Every push to GitHub automatically triggers the `ci.yml` workflow, running all tests on Linux to ensure cross-platform compatibility.
