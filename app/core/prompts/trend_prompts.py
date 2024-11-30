TREND_ANALYSIS_PROMPT = """
    Analyze current trends for ad generation based on the following information:
    Guidelines: {guidelines}
    Region: {region}
    Campaign Details: {campaign}

    Your task is to:
    1. Identify key market trends relevant to the campaign
    2. Extract target audience preferences
    3. Analyze competitor strategies
    4. Determine optimal ad messaging approach

    Provide a structured analysis following the exact format specified in the format instructions below.
    Make sure to include all required fields and format them according to the schema.

    Format the extracted information in the following JSON structure:
    {format_instructions}
"""

TREND_REFINEMENT_PROMPT = """
    Given the raw trend data, format it for image generation:
    {trend_data}

    Consider:
    1. Visual elements that represent identified trends
    2. Color schemes that resonate with the target audience
    3. Composition elements that align with competitor analysis
    4. Key messaging points to incorporate

    Provide a structured output focusing on visual elements and composition.
    """
