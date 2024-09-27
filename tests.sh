curl -X GET "http://localhost:8000/v1/health" -H "Content-Type: application/json"

curl -X GET "http://localhost:8000/v1/models" -H "Content-Type: application/json"

curl -X POST "http://localhost:8000/v1/vision/inference" \
    -H "Content-Type: application/json" \
    -d '{
          "image_base64": ["<your_base64_encoded_image>"],
          "model_name": "resnet50"
        }'


curl -X POST "http://localhost:8000/v1/vision/inference/multiple" \
    -H "Content-Type: application/json" \
    -d '{
          "image_base64": [
            "<your_base64_encoded_image_1>",
            "<your_base64_encoded_image_2>"
          ],
          "model_name": "efficientnet_b0"
        }'


curl -X GET "http://localhost:8000/v1/usage" -H "Content-Type: application/json"