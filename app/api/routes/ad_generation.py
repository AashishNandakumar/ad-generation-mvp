from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ...models.schemas import AdGenerationRequest, GeneratedAd
from ...core.utils.file_processor import FileProcessor
from ...core.agents.trend_agent import TrendAgent
from ...core.agents.image_agent import ImageAgent

router = APIRouter()
file_processor = FileProcessor()
trend_agent = TrendAgent()
image_agent = ImageAgent()


@router.post("/extract")
def extract_data(
    guidelines: UploadFile = File(...),
    brand_metadata: UploadFile = File(...),
    campaign_details: UploadFile = File(...),
    design_plan: UploadFile = File(...),
    region: str = Form(...),
):
    try:
        processed_data = {
            "guidelines": file_processor.process_file(guidelines),
            "brand_metadata": file_processor.process_file(brand_metadata),
            "campaign_details": file_processor.process_file(campaign_details),
            "design_plan": file_processor.process_file(design_plan),
            "region": region,
        }
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-ad", response_model=GeneratedAd)
def generate_ad(data: AdGenerationRequest):
    try:
        # Analyze trends using TrendAgent
        trend_analysis = trend_agent.analyze_trends(
            data.guidelines, data.region, data.campaign_details
        )

        # print(f"output of agent1: {trend_analysis}")

        # Generate images using ImageAgent
        generated_images = image_agent.generate_images(
            trend_analysis, data.design_plan, data.brand_metadata
        )

        return GeneratedAd(
            image_urls=generated_images, metadata={"trend_analysis": trend_analysis}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
