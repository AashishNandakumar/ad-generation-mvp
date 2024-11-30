from typing import Dict, Any
import json


class DataFormatter:
    @staticmethod
    async def format_trend_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trend data for image generation."""
        try:
            formatted_data = {
                "market_trends": raw_data.get("market_trends", []),
                "audience_insights": raw_data.get("audience_insights", {}),
                "visual_elements": await DataFormatter._extract_visual_elements(
                    raw_data
                ),
                "composition_guidelines": await DataFormatter._create_composition_guidelines(
                    raw_data
                ),
            }
            return formatted_data
        except Exception as e:
            raise ValueError(f"Error formatting trend data: {str(e)}")

    @staticmethod
    async def format_brand_guidelines(brand_data: str) -> Dict[str, Any]:
        """Format brand guidelines for image generation."""
        try:
            parsed_data = (
                json.loads(brand_data) if isinstance(brand_data, str) else brand_data
            )
            return {
                "colors": await DataFormatter._parse_colors(parsed_data),
                "typography": await DataFormatter._parse_typography(parsed_data),
                "logo": await DataFormatter._parse_logo_requirements(parsed_data),
                "brand_voice": parsed_data.get("brand_voice", {}),
            }
        except Exception as e:
            raise ValueError(f"Error formatting brand guidelines: {str(e)}")

    @staticmethod
    async def _extract_visual_elements(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure visual elements from trend data."""
        return {
            "primary_elements": data.get("visual_elements", {}).get("primary", []),
            "secondary_elements": data.get("visual_elements", {}).get("secondary", []),
            "background": data.get("visual_elements", {}).get("background", {}),
            "layout_preferences": data.get("visual_elements", {}).get("layout", {}),
        }

    @staticmethod
    async def _create_composition_guidelines(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create composition guidelines from trend data."""
        return {
            "layout": data.get("composition", {}).get("layout", "balanced"),
            "focal_points": data.get("composition", {}).get("focal_points", []),
            "hierarchy": data.get("composition", {}).get("hierarchy", []),
            "spacing": data.get("composition", {}).get("spacing", {}),
        }

    @staticmethod
    async def _parse_colors(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse color information from brand guidelines."""
        return {
            "primary": data.get("colors", {}).get("primary", []),
            "secondary": data.get("colors", {}).get("secondary", []),
            "accent": data.get("colors", {}).get("accent", []),
        }

    @staticmethod
    async def _parse_typography(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse typography information from brand guidelines."""
        return {
            "primary_font": data.get("typography", {}).get("primary_font", ""),
            "secondary_font": data.get("typography", {}).get("secondary_font", ""),
            "font_sizes": data.get("typography", {}).get("sizes", {}),
        }

    @staticmethod
    async def _parse_logo_requirements(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse logo requirements from brand guidelines."""
        return {
            "placement": data.get("logo", {}).get("placement", "top-left"),
            "size": data.get("logo", {}).get("size", "medium"),
            "clearspace": data.get("logo", {}).get("clearspace", "10%"),
        }
