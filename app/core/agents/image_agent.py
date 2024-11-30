# import json
# from typing import List, Dict, Any
# from aioboto3 import Session
# from langchain.prompts import PromptTemplate
# from ..prompts.image_prompts import IMAGE_GENERATION_PROMPT, IMAGE_REFINEMENT_PROMPT
# from ...config import settings


# class ImageAgent:
#     def __init__(self):
#         self.session = Session()  # Create a session instance

#     async def generate_images(
#         self,
#         trend_data: Dict[str, Any],
#         design_plan: str,
#         brand_metadata: str,
#     ) -> List[str]:
#         # Use the session to create a client
#         async with self.session.client(
#             service_name="bedrock-runtime",
#             region_name=settings.AWS_REGION,
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             aws_session_token=settings.AWS_SESSION_TOKEN,
#         ) as client:
#             try:
#                 # Format the prompt
#                 prompt_template = PromptTemplate(
#                     template=IMAGE_GENERATION_PROMPT,
#                     input_variables=[
#                         "trend_data",
#                         "design_plan",
#                         "brand_metadata",
#                         "format",
#                     ],
#                 )

#                 formatted_prompt = prompt_template.format(
#                     trend_data=json.dumps(trend_data),
#                     design_plan=design_plan,
#                     brand_metadata=brand_metadata,
#                     format="1024x1024",
#                 )

#                 # Generate multiple images
#                 image_urls = []
#                 for _ in range(2):
#                     response = await self._generate_single_image(
#                         client, formatted_prompt
#                     )
#                     image_urls.append(response)

#                 return image_urls

#             except Exception as e:
#                 raise Exception(f"Error generating images: {str(e)}")

#     async def refine_image(
#         self, image_data: str, refinement_params: Dict[str, Any]
#     ) -> str:
#         async with self.session.client(
#             service_name="bedrock-runtime",
#             region_name=settings.AWS_REGION,
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         ) as client:
#             try:
#                 prompt_template = PromptTemplate(
#                     template=IMAGE_REFINEMENT_PROMPT,
#                     input_variables=[
#                         "composition_details",
#                         "color_requirements",
#                         "placement_guidelines",
#                     ],
#                 )

#                 refinement_prompt = prompt_template.format(
#                     composition_details=refinement_params.get("composition", ""),
#                     color_requirements=refinement_params.get("colors", ""),
#                     placement_guidelines=refinement_params.get("placement", ""),
#                 )

#                 return await self._generate_single_image(client, refinement_prompt)

#             except Exception as e:
#                 raise Exception(f"Error refining image: {str(e)}")

#     async def _generate_single_image(self, client, prompt: str) -> str:
#         try:
#             response = await client.invoke_model(
#                 modelId="stability.sd3-large-v1:0",
#                 body=json.dumps(
#                     {
#                         "text_prompts": [{"text": prompt}],
#                         "cfg_scale": 10,
#                         "steps": 50,
#                         "seed": 42,
#                         "width": 1024,
#                         "height": 1024,
#                     }
#                 ),
#             )

#             response_body = json.loads(await response["body"].read())
#             image_data = response_body["artifacts"][0]["base64"]
#             return f"data:image/png;base64,{image_data}"

#         except Exception as e:
#             raise Exception(f"Error generating single image: {str(e)}")

import json
import base64
from typing import List, Dict, Any
import boto3
from langchain.prompts import PromptTemplate
from ..prompts.image_prompts import IMAGE_GENERATION_PROMPT, IMAGE_REFINEMENT_PROMPT
from ...config import settings


class ImageAgent:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            # aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    async def generate_images(
        self,
        trend_data: Dict[str, Any],
        design_plan: str,
        brand_metadata: str,
    ) -> List[str]:
        """Generate images using AWS Bedrock."""
        try:
            # Format the prompt
            prompt_template = PromptTemplate(
                template=IMAGE_GENERATION_PROMPT,
                input_variables=[
                    "trend_data",
                    "design_plan",
                    "brand_metadata",
                    "format",
                ],
            )

            formatted_prompt = prompt_template.format(
                trend_data=json.dumps(trend_data),
                design_plan=design_plan,
                brand_metadata=json.dumps(brand_metadata),
                format="1024x1024",
            )

            # Generate multiple images
            image_urls = []
            for _ in range(2):  # Generate 2 images
                response = await self._generate_single_image(formatted_prompt)
                image_urls.append(response)

            return image_urls

        except Exception as e:
            raise Exception(f"Error generating images: {str(e)}")

    async def _generate_single_image(self, prompt: str) -> str:
        """Generate a single image using AWS Bedrock."""
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId="amazon.titan-image-generator-v1",
                body=json.dumps(
                    {
                        "taskType": "TEXT_IMAGE",
                        "textToImageParams": {
                            "text": prompt,
                            "numberOfImages": 1,
                            "width": 1024,
                            "height": 1024,
                            "quality": "standard",
                            "seed": 42,  # Optional
                        },
                        "imageGenerationConfig": {"cfgScale": 8.0, "steps": 50},
                    }
                ),
            )

            # Process the response
            response_body = json.loads(response["body"].read().decode("utf-8"))
            image_data = response_body["images"][0]

            # For MVP, returning base64
            return f"data:image/png;base64,{image_data}"

        except Exception as e:
            raise Exception(f"Error generating single image: {str(e)}")

    async def refine_image(
        self, image_data: str, refinement_params: Dict[str, Any]
    ) -> str:
        """Refine generated image based on feedback."""
        try:
            prompt_template = PromptTemplate(
                template=IMAGE_REFINEMENT_PROMPT,
                input_variables=[
                    "composition_details",
                    "color_requirements",
                    "placement_guidelines",
                ],
            )

            refinement_prompt = prompt_template.format(
                composition_details=refinement_params.get("composition", ""),
                color_requirements=refinement_params.get("colors", ""),
                placement_guidelines=refinement_params.get("placement", ""),
            )

            # Generate refined image
            return await self._generate_single_image(refinement_prompt)

        except Exception as e:
            raise Exception(f"Error refining image: {str(e)}")
