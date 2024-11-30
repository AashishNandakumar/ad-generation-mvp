import json
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from ..prompts.image_prompts import IMAGE_GENERATION_PROMPT, IMAGE_REFINEMENT_PROMPT
from ...config import settings

from together import Together
from dotenv import load_dotenv

load_dotenv()


class ImageAgent:
    def __init__(self):
        # self.bedrock_runtime = boto3.client(
        #     service_name="bedrock-runtime",
        #     region_name=settings.AWS_REGION,
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        #     # aws_session_token=settings.AWS_SESSION_TOKEN,
        # )
        self.flux_client = Together(
            api_key="42694f97a14e4e1cb7c1725006468dd05229cc0927838e3edb5229a2aefa9a75"
        )

    def generate_images(
        self,
        trend_data: Dict[str, Any],
        design_plan: str,
        brand_metadata: str,
    ):
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
                response = self._generate_single_image(formatted_prompt)
                image_urls.append(response)
            print("image urls: ", image_urls)
            return image_urls

        except Exception as e:
            raise Exception(f"Error generating images: {str(e)}")

    def _generate_single_image(self, prompt: str):
        """Generate a single image using AWS Bedrock."""
        try:
            print(f"prompt passed to image agent: {prompt}")

            # request_body = {
            #     "taskType": "TEXT_IMAGE",
            #     "textToImageParams": {"text": prompt},
            #     "imageGenerationConfig": {
            #         "numberOfImages": 1,
            #         "height": 1024,
            #         "width": 1024,
            #         "cfgScale": 8.0,
            #     },
            # }

            # response = self.bedrock_runtime.invoke_model(
            #     modelId="amazon.titan-image-generator-v1", body=json.dumps(request_body)
            # )

            # response_body = json.loads(response["body"].read().decode("utf-8"))
            # return f"data:image/png;base64,{response_body['images'][0]}"

            response = self.flux_client.images.generate(
                prompt="""Brand Essentials:

                Brand: Zomato
                Tagline: "Discover great food & drinks"
                Brand Voice: Friendly, foodie-focused, quirky
                Core Values: Passion for food, customer satisfaction, innovation

                Visual Guidelines:

                Color Palette:
                Primary: Red (#CB202D), White (#FFFFFF)
                Secondary: Black, Gray (#E23744)
                Typography:
                Headings: Proxima Nova Bold
                Body: Open Sans Regular
                Imagery: Vibrant food photography, lifestyle images

                Target Audience:

                Demographics: Adults 18-45, urban, middle to upper-middle income
                Psychographics: Food enthusiasts, busy professionals
                Locations: Major cities
                Behavioral: Mobile app users, social media active

                Campaign Objectives:

                Increase app downloads
                Boost order frequency
                Key Messaging: Variety of cuisines, quick delivery
                Call to Action: "Order Now", "Explore Restaurants"

                Key Requirements:

                Follow brand color scheme
                Include red circular logo with white fork
                Maintain visual hierarchy
                Professional, high-resolution (1024x1024)
                Square format for Instagram""",
                model="black-forest-labs/FLUX.1-dev",
                steps=50,
                n=1,
            )
            print("response from image generator: ", response)
            urls = []

            for item in response.data:
                # print("item: ", item)
                if hasattr(item, "url"):
                    urls.append(item.url)

            # return {"image_urls": urls, "metadata": {}}
        except Exception as e:
            raise Exception(f"Error generating single image: {str(e)}")

    def refine_image(self, image_data: str, refinement_params: Dict[str, Any]) -> str:
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
            return self._generate_single_image(refinement_prompt)

        except Exception as e:
            raise Exception(f"Error refining image: {str(e)}")
