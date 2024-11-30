from typing import Dict, Any
from langchain.agents import initialize_agent, Tool
from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from ..prompts.trend_prompts import TREND_ANALYSIS_PROMPT, TREND_REFINEMENT_PROMPT
from ..utils.data_formatter import DataFormatter
from ...config import settings
import tavily
import json


class TrendAnalysis(BaseModel):
    market_trends: List[str] = Field(description="List of current market trends")
    audience_insights: Dict[str, Any] = Field(
        description="Target audience preferences and behaviors"
    )
    competitor_analysis: List[Dict[str, str]] = Field(
        description="Analysis of competitor strategies"
    )
    messaging_strategy: Dict[str, Any] = Field(
        description="Optimal ad messaging approach"
    )


class TrendAgent:
    def __init__(self):
        self.tavily_client = tavily.Client(api_key=settings.TAVILY_API_KEY)
        self.llm = Bedrock(
            credentials_profile_name="default",
            model_id="amazon.titan-text-lite-v1",
            region_name=settings.AWS_REGION,
        )
        self.data_formatter = DataFormatter()
        self.output_parser = PydanticOutputParser(pydantic_object=TrendAnalysis)

        self.tools = [
            Tool(
                name="Trend Search",
                func=self._search_trends,
                description="Search for current trends in a specific region and industry",
            ),
            Tool(
                name="Format Data",
                func=self._format_trend_data,
                description="Format trend data for image generation",
            ),
        ]

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True,
        )

    async def _search_trends(self, query: str) -> Dict[str, Any]:
        """Search for trends using Tavily API."""
        try:
            response = await self.tavily_client.search(query)
            return self._process_search_results(response)
        except Exception as e:
            raise Exception(f"Error searching trends: {str(e)}")

    def _process_search_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure search results."""
        processed_results = {
            "market_trends": [],
            "audience_insights": {},
            "competitor_analysis": [],
        }

        for result in results.get("results", []):
            # Categorize and structure the results
            if "market" in result.get("title", "").lower():
                processed_results["market_trends"].append(
                    {"title": result.get("title"), "summary": result.get("summary")}
                )
            elif "audience" in result.get("title", "").lower():
                processed_results["audience_insights"].update(
                    {"insight": result.get("summary")}
                )
            elif "competitor" in result.get("title", "").lower():
                processed_results["competitor_analysis"].append(
                    {
                        "competitor": result.get("title"),
                        "strategy": result.get("summary"),
                    }
                )

        return processed_results

    async def _format_trend_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trend data for image generation."""
        return await self.data_formatter.format_trend_data(data)

    async def analyze_trends(
        self, guidelines: str, region: str, campaign_details: str
    ) -> Dict[str, Any]:
        """Analyze trends and format for image generation."""
        try:
            # Create analysis prompt with output parser
            prompt = PromptTemplate(
                template=TREND_ANALYSIS_PROMPT + "\n{format_instructions}",
                input_variables=["guidelines", "region", "campaign"],
                partial_variables={
                    "format_instructions": self.output_parser.get_format_instructions()
                },
            )

            # Run initial analysis
            chain = LLMChain(llm=self.llm, prompt=prompt)
            print(chain)
            analysis_response = await chain.arun(
                guidelines=guidelines, region=region, campaign=campaign_details
            )
            print(f"a-{analysis_response}")
            # Parse the response using the output parser
            parsed_response = self.output_parser.parse(analysis_response)
            print(parsed_response)

            # Convert to dictionary
            trend_data = parsed_response.dict()

            # Search for additional trend data
            search_query = f"latest advertising trends {region} {trend_data.get('market_trends', [''])[0]}"
            search_results = await self._search_trends(search_query)

            # Combine and format results
            combined_data = {**trend_data, "search_insights": search_results}

            # Format data for image generation
            return await self._format_trend_data(combined_data)

        except Exception as e:
            raise Exception(f"Error analyzing trends: {str(e)}")
