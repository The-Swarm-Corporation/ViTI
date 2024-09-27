

# ViTI - Vision Transformer Inference Server

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)


[![Build Status](https://img.shields.io/github/workflow/status/The-Swarm-Corporation/ViTI/CI)](https://github.com/The-Swarm-Corporation/ViTI/actions)
[![License](https://img.shields.io/github/license/The-Swarm-Corporation/ViTI)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/The-Swarm-Corporation/ViTI)](https://github.com/The-Swarm-Corporation/ViTI/stargazers)

**ViTI** is a **high-performance, production-grade inference server** for Vision Transformer (ViT) models and other state-of-the-art architectures from the `timm` library. Built with **FastAPI**, ViTI supports dynamic model loading, concurrent image processing, and an enterprise-level cost calculation system based on model complexity, image count, and processing time.

## Key Features

- **Dynamic Model Inference**: Load and run any vision model from the `timm` library.
- **Concurrent Image Processing**: Supports multiple image processing simultaneously, taking full advantage of your CPU cores.
- **Enterprise-Grade Cost Calculation**: Scalable pricing based on model size, number of images, and processing time.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+.
- **Loguru Logging**: For robust, customizable, and readable logging throughout the inference process.
- **Pydantic**: Ensures fast and accurate data validation, guaranteeing reliability in production environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Cost Calculation](#cost-calculation)
- [Docker Support](#docker-support)
- [License](#license)
- [Contributing](#contributing)

## Quick Start

Follow the steps below to get started with ViTI.

### Prerequisites

- Python 3.7+
- `pip` for managing Python packages
- `git` to clone the repository

### Clone the Repository

```bash
git clone https://github.com/The-Swarm-Corporation/ViTI.git
cd ViTI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the API Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will now be running at `http://localhost:8000`.

### Example cURL Request

Single image inference using `resnet50`:

```bash
curl -X POST "http://localhost:8000/v1/vision/inference" \
    -H "Content-Type: application/json" \
    -d '{
          "image_base64": ["<your_base64_encoded_image>"],
          "model_name": "resnet50"
        }'
```

Multiple image inference:

```bash
curl -X POST "http://localhost:8000/v1/vision/inference/multiple" \
    -H "Content-Type: application/json" \
    -d '{
          "image_base64": ["<your_base64_encoded_image_1>", "<your_base64_encoded_image_2>"],
          "model_name": "efficientnet_b0"
        }'
```

## Installation

You can install ViTI via **pip** using the provided `requirements.txt` or manually by installing the following:

- **FastAPI**: The core web framework.
- **Uvicorn**: ASGI server for high-performance API deployment.
- **Torch**: For deep learning model inference.
- **Timm**: Access to hundreds of pre-trained vision models.
- **Loguru**: For logging.

```bash
pip3 install -r requirements.txt
```

## API Endpoints

### Health Check

- **Endpoint**: `/v1/health`
- **Method**: `GET`
- **Description**: Check the health of the API server.
- **Response**:
  ```json
  {
    "status": "ok",
    "time": "2024-09-27 10:30:00"
  }
  ```

### List Available Models

- **Endpoint**: `/v1/models`
- **Method**: `GET`
- **Description**: Get a list of available models from the `timm` library.
- **Response**:
  ```json
  [
    "resnet50",
    "efficientnet_b0",
    "mobilenetv2_100"
  ]
  ```

### Inference on a Single Image

- **Endpoint**: `/v1/vision/inference`
- **Method**: `POST`
- **Description**: Run inference on a single image.
- **Request Body**:
  ```json
  {
    "image_base64": ["<base64_encoded_image>"],
    "model_name": "resnet50"
  }
  ```
- **Response**:
  ```json
  {
    "logits": [[0.45, 0.35, 0.1, 0.05, 0.05]],
    "top_5_classes": [["class_23", "class_34", "class_5", "class_101", "class_56"]],
    "cost": 0.02
  }
  ```

### Inference on Multiple Images

- **Endpoint**: `/v1/vision/inference/multiple`
- **Method**: `POST`
- **Description**: Run inference on multiple images concurrently.
- **Request Body**:
  ```json
  {
    "image_base64": ["<base64_encoded_image_1>", "<base64_encoded_image_2>"],
    "model_name": "efficientnet_b0"
  }
  ```
- **Response**:
  ```json
  {
    "logits": [[0.45, 0.35, 0.1], [0.55, 0.15, 0.12]],
    "top_5_classes": [["class_23", "class_34", "class_5"], ["class_12", "class_56", "class_78"]],
    "cost": 0.03
  }
  ```

## Cost Calculation

ViTI implements a dynamic pricing model based on:
- **Number of Images**: Each additional image increases the cost.
- **Model Size**: Models with more parameters incur higher costs.
- **Processing Time**: Longer inference times increase the cost.

**Cost Formula**:

```text
cost = base_cost + (image_count * image_cost) + (processing_time * time_cost) + (log(model_size) * model_size_factor)
```

Where:
- `base_cost`: A fixed base cost ($0.01).
- `image_cost`: Cost per image ($0.01).
- `time_cost`: $0.01 per second of inference time.
- `model_size_factor`: A scaling factor for model size ($0.0001 * log(model size)).

### Example Cost Calculation

For 2 images using `efficientnet_b0`:
- Number of images: 2
- Model size: 5.3M parameters
- Processing time: 2 seconds

```
cost = 0.01 + (2 * 0.01) + (2 * 0.01) + (log(5288548) * 0.0001)
cost ≈ 0.06
```

## Docker Support

You can run ViTI using **Docker** to easily deploy the inference server in a containerized environment.

### Dockerfile

```dockerfile
# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and run the server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Build and Run the Docker Image

```bash
docker build -t viti-inference .
docker run -d -p 8000:8000 viti-inference
```

## License

ViTI is released under the [MIT License](LICENSE).

## Contributing

We welcome contributions from the community! Please read our [contributing guide](CONTRIBUTING.md) for more information.

---

This README.md provides a comprehensive, professional, and structured overview of ViTI, aimed at both developers and enterprise users. It includes detailed sections on getting started, usage, API endpoints, cost calculations, and Docker deployment, making it ready for production-level deployments.
