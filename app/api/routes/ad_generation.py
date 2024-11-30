from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ...models.schemas import AdGenerationRequest, GeneratedAd

# from app.models.schemas import AdGenerationRequest, GeneratedAd
from ...core.utils.file_processor import FileProcessor
from ...core.agents.trend_agent import TrendAgent
from ...core.agents.image_agent import ImageAgent

from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate

from operator import imod

# together import
from together import Together

# from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
file_processor = FileProcessor()
trend_agent = TrendAgent()
image_agent = ImageAgent()


@router.post("/extract")
async def extract_data(
    guidelines: UploadFile = File(...),
    brand_metadata: UploadFile = File(...),
    campaign_details: UploadFile = File(...),
    design_plan: UploadFile = File(...),
    region: str = Form(...),
):
    """
    Extract text from uploaded files and process them.

    Args:
        guidelines (UploadFile): Guidelines document
        brand_metadata (UploadFile): Brand metadata document
        campaign_details (UploadFile): Campaign details document
        design_plan (UploadFile): Design plan document
        region (str): Region information
    """
    try:
        processed_data = {
            "guidelines": await file_processor.process_file(guidelines),
            "brand_metadata": await file_processor.process_file(brand_metadata),
            "campaign_details": await file_processor.process_file(campaign_details),
            "design_plan": await file_processor.process_file(design_plan),
            "region": region,
        }
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-ad", response_model=GeneratedAd)
async def generate_ad(data: AdGenerationRequest):
    # try:
    #     # print(data)
    #     # Analyze trends using Agent1
    #     trend_analysis = await trend_agent.analyze_trends(
    #         data.guidelines, data.region, data.campaign_details
    #     )

    #     print(trend_analysis)

    #     # Generate images using Agent2
    #     generated_images = await image_agent.generate_images(
    #         trend_analysis, data.design_plan, data.brand_metadata
    #     )

    #     return GeneratedAd(
    #         image_urls=generated_images, metadata={"trend_analysis": trend_analysis}
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    model = ChatBedrock(
        model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        beta_use_converse_api=True,
        region="us-west-2",
    )

    prompt = (
        PromptTemplate.from_template(
            "You are provided with the campaign details which are as follows:\n\nCampaign details: {campaign_details}, for the brand: {brand}."
        )
        + "\n\nI want you to refine the campaign details, taking reference to the provided guideline as well as the brand details which are as follows:\n\nGuidelines: {guidelines}."
        + "\n\nEnsure the refined campaign details are output in the following structured format, adhering to the specified sections and focusing on readability:"
        + "\n\nPrompt Template for Poster Generation:"
        + "\n\nTitle of the Image:"
        + '\n"[Title of the Campaign] - A vibrant and engaging poster for [campaign details]."'
        + "\n\nCampaign Details of the Image:"
        + "\nCreate a visually appealing ad campaign poster for [brand or campaign, e.g., Zomato's New Year celebration offer]."
        + "\nThe campaign is targeted at [target audience, e.g., young professionals and families] in [location, e.g., Mumbai, India]."
        + '\nHighlight the key message: [e.g., "Celebrate the New Year with Zomato - Delicious Discounts Await!"].'
        + "\n\nTarget Audience Location:"
        + "\nThe design should reflect the essence of [location, e.g., Mumbai's urban vibrancy and lively streets]."
        + "\nUse elements that represent [local culture, landmarks, or relevant imagery, e.g., Marine Drive, food, fireworks]."
        + "\n\nTrending Topic in that Location:"
        + "\nIncorporate the trending topic of [e.g., festive New Year celebrations or food festivals in Mumbai]."
        + "\nShowcase [specific trends, e.g., street food, restaurant discounts, or festive decorations]."
        + "\n\nSome More Context About the Trending Topic:"
        + "\nHighlight the theme of [e.g., celebration, togetherness, and indulgence in delicious cuisines]."
        + "\nCapture the excitement and anticipation of [event, e.g., New Year's Eve parties] that is trending in [location]."
        + "\n\nPreferences for Text Placement:"
        + '\n- The headline text ("[e.g., Celebrate with Zomato]") should be bold and centered at the top.'
        + '\n- The key offer ("[e.g., Flat 50% off on meals]") should be prominent and placed in the center or highlighted with vibrant colors.'
        + '\n- The call-to-action text ("[e.g., Download the app now!]") should be placed at the bottom with a clear and actionable design.'
        + "\n- Leave enough whitespace for readability and balance between text and visuals."
        + "\n\nOverall Style and Design Preferences:"
        + "\n- Use a modern, festive color palette (e.g., red, gold, and black for New Year)."
        + "\n- Incorporate relevant icons, such as [fireworks, food items, or celebratory motifs]."
        + "\n- Blend clean fonts with subtle graphics to maintain elegance and focus on the brand message."
        + "\n\nImportant Note for Image Generation Model:"
        + "\n- Ensure there are absolutely no spelling or grammatical errors in the text on the image. Double-check all words, as the image is for a professional ad campaign."
        + "\n- The final image must balance text and visuals to maintain clarity and engagement."
        + "\n\nI would like my campaign to cater to local audiences, and one of the best ways to do it is to provide references to current happenings like politics, cricket, kabaddi, pop culture, movies, and shows."
        + "\n\nAlso, you are free to include other aspects that can improve my ad campaign."
    )

    formatted_prompt = prompt.format(
        campaign_details=data.campaign_details,
        guidelines=data.guidelines,
        brand=data.brand_metadata,
    )
    # print(formatted_prompt)

    llm_response = model.invoke(formatted_prompt)
    # return {"data": llm_response}
    print(f"llm-{llm_response.content}-{type(llm_response.content)}")

    image_client = Together(api_key="")
    response = image_client.images.generate(
        prompt=llm_response.content, model="black-forest-labs/FLUX.1-schnell", steps=4
    )

    urls = response.data[0].url

    return {"image_urls": [urls], "metadata": {}}
