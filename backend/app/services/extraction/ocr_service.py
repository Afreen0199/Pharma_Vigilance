import boto3
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                # If explicit keys are in environment, use them. Otherwise rely on default credential chain.
                if self.access_key and self.secret_key:
                    logger.info("Initializing AWS Textract client with environment credentials...")
                    self._client = boto3.client(
                        'textract',
                        aws_access_key_id=self.access_key,
                        aws_secret_access_key=self.secret_key,
                        region_name=self.region
                    )
                else:
                    logger.info("Initializing AWS Textract client using default AWS credential chain...")
                    self._client = boto3.client('textract', region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to initialize AWS Textract client: {e}")
                raise e
        return self._client

    def extract_text(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Sends raw or preprocessed image bytes to AWS Textract detect_document_text API.
        
        :param image_bytes: Image file bytes
        :return: Tuple containing:
                 - Extracted text string (lines joined by newlines)
                 - Average confidence score (between 0.0 and 1.0)
        """
        try:
            response = self.client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            lines = []
            confidences = []
            
            for block in response.get("Blocks", []):
                if block.get("BlockType") == "LINE":
                    text = block.get("Text", "")
                    if text:
                        lines.append(text)
                        if "Confidence" in block:
                            confidences.append(block["Confidence"] / 100.0) # Map to 0.0 - 1.0
                            
            full_text = "\n".join(lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
            
            logger.info(f"AWS Textract extracted {len(lines)} lines of text with average confidence {avg_confidence:.4f}")
            return full_text, round(avg_confidence, 4)
            
        except Exception as e:
            logger.error(f"Error calling AWS Textract: {e}")
            raise e

ocr_service_instance = OCRService()
