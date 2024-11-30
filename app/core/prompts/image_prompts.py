IMAGE_GENERATION_PROMPT = """
Generate an advertising image based on:
Trend Data: {trend_data}
Design Plan: {design_plan}
Brand Guidelines: {brand_metadata}

Key Requirements:
1. Follow brand color scheme and typography
2. Incorporate specified logo placement
3. Maintain visual hierarchy according to design plan
4. Ensure messaging alignment with trend analysis

The image should be high-resolution, professional, and optimized for {format}.
"""

IMAGE_REFINEMENT_PROMPT = """
Refine the generated image considering:
1. Brand consistency
2. Message clarity
3. Visual impact
4. Technical specifications

Adjust:
- Composition: {composition_details}
- Color balance: {color_requirements}
- Element placement: {placement_guidelines}
"""
