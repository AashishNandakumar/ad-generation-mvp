# from langchain_community.document_loaders import PyPDFLoader
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os


load_dotenv()

with open("misc/brand.txt", "r", encoding="utf-8") as brand_file:
    brand = brand_file.read()

with open("misc/campaign.txt", "r", encoding="utf-8") as campaign_file:
    campaign = campaign_file.read()

with open("misc/guidelines.txt", "r", encoding="utf-8") as guidelines_file:
    guidelines = guidelines_file.read()

# loader = PyPDFLoader(
#     "misc/bedrock_docs.pdf"
# )

# pages = []
# for doc in loader.lazy_load():
#     pages.append(doc)
#     if len(pages) >= 10:
#         # do some paged operation, e.g.
#         # index.upsert(page)

#         pages = []
# len(pages)

model = ChatBedrock(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    beta_use_converse_api=True,
)

# guidelines = """
# 1. Focus on convenience and time-saving aspects of the service
# 2. Highlight the variety of cuisines and restaurants available
# 3. Emphasize the user-friendly mobile app and website interface
# 4. Showcase the reliability and punctuality of delivery drivers
# 5. Incorporate customer testimonials and satisfaction ratings
# 6. Promote any unique features or benefits (e.g., real-time tracking, customizable orders)
# 7. Use vibrant food imagery to appeal to viewers' appetites
# 8. Highlight any promotional offers or loyalty programs
# 9. Emphasize the service's commitment to food safety and hygiene
# 10. Showcase the local aspect by featuring popular neighborhood restaurants
# """

# campaign_details = """
# Campaign Name: "Feast at Your Fingertips"

# 1. Core Message:
# "From craving to dining in minutes - [Your Service Name] brings the city's best to your doorstep."

# 2. Visual Theme:
# Vibrant, high-quality images of diverse cuisines, happy customers receiving deliveries, and satisfied families enjoying meals together.

# 3. Key Campaign Elements:

# a) Convenience Spotlight:
# - 30-second video ad showing a busy professional ordering lunch, tracking the delivery in real-time, and receiving it just as a meeting ends.
# - Tagline: "Your time is precious. We deliver."

# b) Cuisine Variety Showcase:
# - Series of social media posts featuring "Cuisine of the Week," highlighting different restaurant partners.
# - Interactive website feature allowing users to "travel the world" through local restaurant offerings.

# c) App-centric Promotion:
# - Tutorial-style ads demonstrating the ease of using the app, from browsing to ordering to tracking.
# - Push notification campaign: "Dinner is just 3 taps away!"

# d) Reliability Promise:
# - Feature top-rated delivery drivers in "Meet Your Delivery Hero" social media series.
# - Implement and promote a "On-Time Guarantee" policy.

# e) Customer Testimonials:
# - User-generated content campaign encouraging customers to share their [Your Service Name] stories.
# - Showcase real customer reviews in all advertising materials.

# f) Unique Features Highlight:
# - Promote the ability to customize orders with "Have It Your Way" messaging.
# - Emphasize real-time tracking with "Watch Your Food's Journey" feature ads.

# g) Food Safety Assurance:
# - Create a "Safety Seal" graphic to be featured on all packaging.
# - Launch a "Kitchen to Couch" video series showcasing hygiene practices.

# h) Local Focus:
# - Partner with local food bloggers for "Hidden Gem" restaurant features.
# - Create neighborhood-specific promotions and restaurant recommendations.

# 4. Promotional Offers:
# - Launch campaign with "First Delivery Free" offer for new users.
# - Implement a points-based loyalty program: "Feast Rewards"

# 5. Multi-channel Approach:
# - Social Media: Instagram, Facebook, TikTok for food imagery and quick video content.
# - TV and Streaming Services: 30-second ads during prime time and food-related shows.
# - Radio: Drive-time ads focusing on convenience for commuters.
# - Out-of-Home: Bus stop and billboard ads in busy urban areas.

# 6. Measurement Metrics:
# - App downloads and active users
# - Order frequency and average order value
# - Customer retention rates
# - Social media engagement and sentiment
# - Brand awareness surveys

# This campaign aims to position your food delivery service as a convenient, reliable, and diverse option that seamlessly integrates into customers' daily lives, while also supporting local businesses and ensuring food safety.
# """

prompt = (
    PromptTemplate.from_template(
        "You are provided with the campaign details which are as follows. Campaign details: {campaign_details}"
    )
    + ", for the brand: {brand}"
    + ", I want you to refine the campaign details, taking reference to the provided guideline as well as the brand details which is as follows. Guidelines: {guidelines}"
    + "\n\nI would like my campaign to cater to local audiences and one of the best way to do it is to provide references to current happenings like politics, cricket, kabaddi, pop culture, movies and shows"
    + "\n\nAlso you are free to include other aspects which can improve my add campaign"
    + "\n\nYou are supposed to return the refined campaign details in markdown code, clearly format the markdown code focusing more on its readability, make sure to provide nothing else "
)

formatted_prompt = prompt.format(
    campaign_details=campaign, guidelines=guidelines, brand=brand
)

llm_response = model.invoke("Say hello in hindi")

# with open("test.md", "w", encoding="utf-8") as file:
#     file.write(llm_response.content)
print(llm_response)


# print("Content: \n")
# print(llm_response.content)

# print("\nResponse Metadata: \n")
# print(llm_response.response_metadata)
