import os
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import timm
import torch
from PIL import Image
from torchvision import transforms
from io import BytesIO
import base64
from loguru import logger
from typing import List, Dict
import uuid

# FastAPI app initialization
app = FastAPI(debug=True)


# Pydantic models for input and output
class InferenceInput(BaseModel):
    id: str = Field(uuid.uuid4().hex)
    timestamp: str = Field(time.time())
    image_base64: List[str]  # List of base64 encoded images
    model_name: str  # Model name from timm


class InferenceOutput(BaseModel):
    id: str = Field(uuid.uuid4().hex)
    timestamp: str = Field(time.time())
    logits: List[List[float]]
    top_5_classes: List[List[str]]
    cost: float  # Cost of processing the request


# Preprocessing function
def preprocess_image(image_data: str) -> torch.Tensor:
    try:
        image = Image.open(
            BytesIO(base64.b64decode(image_data))
        ).convert("RGB")
        transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )
        return transform(image).unsqueeze(0)
    except Exception as e:
        logger.error(f"Error in preprocessing image: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid image format"
        )


# Postprocessing function
def postprocess_output(
    output_tensor: torch.Tensor,
) -> (List[float], List[str]):
    try:
        probabilities = torch.nn.functional.softmax(
            output_tensor, dim=1
        )[0]
        top_probs, top_indices = torch.topk(probabilities, 5)
        top_probs = top_probs.detach().cpu().tolist()
        top_indices = top_indices.detach().cpu().tolist()
        class_labels = [
            f"class_{i}" for i in top_indices
        ]  # Placeholder for actual class names
        return top_probs, class_labels
    except Exception as e:
        logger.error(f"Error in postprocessing output: {e}")
        raise HTTPException(
            status_code=500, detail="Error in model inference"
        )


# Model inference function
def run_inference(
    model: torch.nn.Module, image_tensor: torch.Tensor
) -> torch.Tensor:
    try:
        with torch.no_grad():
            return model(image_tensor)
    except Exception as e:
        logger.error(f"Error in running inference: {e}")
        raise HTTPException(
            status_code=500, detail="Error in model inference"
        )


# Cost calculation function
def calculate_cost(
    num_images: int, model_name: str, processing_time: float
) -> float:
    # Basic formula: cost = base cost + (processing time factor) + (image count multiplier)
    base_cost = 0.01  # Base cost per request
    time_cost = processing_time * 0.05  # Time cost factor
    image_cost = num_images * 0.02  # Cost per image
    return round(base_cost + time_cost + image_cost, 4)


# Endpoint for processing multiple images concurrently
@app.post(
    "/v1/vision/inference/multiple", response_model=InferenceOutput
)
async def inference_multiple(
    request: InferenceInput,
) -> InferenceOutput:
    logger.info(
        f"Received request to process {len(request.image_base64)} images with model {request.model_name}"
    )

    # Check if the requested model exists
    if request.model_name not in timm.list_models(pretrained=True):
        logger.error(f"Model {request.model_name} not found.")
        raise HTTPException(status_code=404, detail="Model not found")

    # Load the model
    model = timm.create_model(request.model_name, pretrained=True)
    model.eval()

    # Track the start time for cost calculation
    start_time = time.time()

    # Process images concurrently using ThreadPoolExecutor
    num_cores = (
        os.cpu_count() or 1
    )  # Get system's available CPU cores
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [
            executor.submit(
                run_inference, model, preprocess_image(img)
            )
            for img in request.image_base64
        ]

        # Wait for all futures to complete
        results = [future.result() for future in futures]

    # Post-process the outputs
    logits_list = []
    classes_list = []
    for output in results:
        logits, top_classes = postprocess_output(output)
        logits_list.append(logits)
        classes_list.append(top_classes)

    # Calculate processing time and cost
    processing_time = time.time() - start_time
    cost = calculate_cost(
        num_images=len(request.image_base64),
        model_name=request.model_name,
        processing_time=processing_time,
    )

    # Return the inference output and cost
    return InferenceOutput(
        logits=logits_list, top_5_classes=classes_list, cost=cost
    )


# Endpoint for checking the health of the API
@app.get("/v1/health", response_model=Dict[str, str])
async def check_health() -> Dict[str, str]:
    """
    Returns the health status of the API.
    """
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    logger.info("Health check passed.")
    return {"status": "ok", "time": current_time}


# Endpoint for listing available models
@app.get("/v1/models", response_model=List[str])
async def list_models() -> List[str]:
    """
    Returns a list of available TIMM models.
    """
    logger.info("Listing all available models")
    return timm.list_models(pretrained=True)


# Endpoint for tracking usage history
usage_history: List[Dict[str, str]] = []


@app.get("/v1/usage", response_model=List[Dict[str, str]])
async def get_usage_history() -> List[Dict[str, str]]:
    """
    Returns the usage history of the API.
    """
    logger.info("Fetching API usage history.")
    return usage_history


# Endpoint for single image inference
@app.post("/v1/vision/inference", response_model=InferenceOutput)
async def inference_single(
    request: InferenceInput,
) -> InferenceOutput:
    logger.info(f"Received request for model: {request.model_name}")

    # Check if model exists
    if request.model_name not in timm.list_models(pretrained=True):
        logger.error(f"Model {request.model_name} not found.")
        raise HTTPException(status_code=404, detail="Model not found")

    # Preprocess image
    image_tensor: torch.Tensor = preprocess_image(
        request.image_base64[0]
    )

    # Load model (this can be optimized by caching models)
    model: torch.nn.Module = timm.create_model(
        request.model_name, pretrained=True
    )
    model.eval()

    # Run inference
    output: torch.Tensor = run_inference(model, image_tensor)

    # Postprocess output
    top_probs, top_classes = postprocess_output(output)

    # Calculate cost (for single image inference)
    cost = calculate_cost(
        num_images=1, model_name=request.model_name, processing_time=0
    )  # Simplified for single image

    # Prepare response
    response = InferenceOutput(
        logits=[top_probs], top_5_classes=[top_classes], cost=cost
    )

    logger.info(
        f"Inference completed for model: {request.model_name}"
    )
    return response


# Main entry point for running the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, log_level="info"
    )
