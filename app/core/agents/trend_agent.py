from typing import Dict, Any
from langchain.agents import initialize_agent, Tool
from langchain_community.llms import Bedrock
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from langchain_core.runnables import RunnablePassthrough
from ..prompts.trend_prompts import TREND_ANALYSIS_PROMPT
from ..utils.data_formatter import DataFormatter
from ...config import settings
import tavily


class TrendAnalysis(BaseModel):
    market_trends: List[str] = Field(
        default_factory=list, description="List of current market trends"
    )
    audience_insights: Dict[str, Any] = Field(
        default_factory=dict, description="Target audience preferences and behaviors"
    )
    competitor_analysis: List[Dict[str, str]] = Field(
        default_factory=list, description="Analysis of competitor strategies"
    )
    messaging_strategy: Dict[str, Any] = Field(
        default_factory=dict, description="Optimal ad messaging approach"
    )


class TrendAgent:
    def __init__(self):
        self.tavily_client = tavily.Client(api_key=settings.TAVILY_API_KEY)
        self.llm = Bedrock(
            credentials_profile_name="default",
            model_id="meta.llama3-70b-instruct-v1:0",
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

    def _search_trends(self, query: str) -> Dict[str, Any]:
        """Search for trends using Tavily API."""
        try:
            response = self.tavily_client.search(query)
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

        print(f"processes results: {processed_results}")
        return processed_results

    def _format_trend_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format trend data for image generation."""
        return self.data_formatter.format_trend_data(data)

    def analyze_trends(
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
            # Create the chain
            chain = (
                RunnablePassthrough().assign(
                    guidelines=lambda _: guidelines,
                    region=lambda _: region,
                    campaign=lambda _: campaign_details,
                )
                | prompt
                | self.llm
            )

            input_data = {
                "guidelines": guidelines,
                "region": region,
                "campaign": campaign_details,
            }

            analysis_response = chain.invoke(input_data)
            print(f"analysis response: {analysis_response}")

            # Invoke with a dictionary as input
            input_data = {
                "guidelines": guidelines,
                "region": region,
                "campaign": campaign_details,
            }
            print("Analysis response:", analysis_response)

            # # Ensure all fields are present before parsing
            # response_data = {
            #     "market_trends": analysis_response.get("market_trends", []),
            #     "audience_insights": analysis_response.get("audience_insights", {}),
            #     "competitor_analysis": analysis_response.get("competitor_analysis", []),
            #     "messaging_strategy": analysis_response.get("messaging_strategy", {}),
            # }

            parsed_response = self.output_parser.parse(analysis_response)
            print("parsed_respose: ", parsed_response)

            trend_data = parsed_response.dict()
            search_query = f"latest advertising trends {region} {trend_data.get('market_trends', [''])[0]}"
            search_results = self._search_trends(search_query)
            combined_data = {**trend_data, "search_insights": search_results}
            return self._format_trend_data(combined_data)

        except Exception as e:
            raise Exception(f"Error analyzing trends: {str(e)}")
