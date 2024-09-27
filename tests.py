import httpx
import base64
from loguru import logger

BASE_URL = (
    "http://localhost:8000"  # Change to your FastAPI server URL
)


# Function to encode an image to base64
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode(
            "utf-8"
        )
    logger.info(f"Encoded image {image_path} to base64")
    return encoded_string


# Example for calling the inference_multiple endpoint
async def call_inference_multiple(
    image_base64: list, model_name: str
):
    logger.info(
        f"Calling inference_multiple with {len(image_base64)} images and model {model_name}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/vision/inference/multiple",
            json={
                "image_base64": image_base64,
                "model_name": model_name,
            },
        )
        logger.info(
            f"Response: {response.status_code} - {response.json()}"
        )
        return response.json()


# Example for calling the health check endpoint
async def call_check_health():
    logger.info("Calling health check endpoint")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/health")
        logger.info(
            f"Response: {response.status_code} - {response.json()}"
        )
        return response.json()


# Example for calling the list_models endpoint
async def call_list_models():
    logger.info("Calling list models endpoint")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/models")
        logger.info(
            f"Response: {response.status_code} - {response.json()}"
        )
        return response.json()


# Example for calling the get_usage_history endpoint
async def call_get_usage_history():
    logger.info("Calling get usage history endpoint")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/usage")
        logger.info(
            f"Response: {response.status_code} - {response.json()}"
        )
        return response.json()


# Example for calling the inference_single endpoint
async def call_inference_single(image_base64: str, model_name: str):
    logger.info(f"Calling inference_single with model {model_name}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/vision/inference",
            json={
                "image_base64": [image_base64],
                "model_name": model_name,
            },
            timeout=10.0,  # Set timeout to 10 seconds
        )
        logger.info(
            f"Response: {response.status_code} - {response.json()}"
        )
        return response.json()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Encode the image to base64
        image_base64 = [
            encode_image_to_base64("test.png")
        ]  # Encode test.png
        model_name = "convnext_xlarge.fb_in22k_ft_in1k"  # Replace with your actual model name

        # await call_inference_multiple(image_base64, model_name)
        # await call_check_health()
        # await call_list_models()
        await call_get_usage_history()
        # await call_inference_single(image_base64[0], model_name)

    asyncio.run(main())
