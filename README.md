# TripPlannerAI

Trip planning website source code - currently WIP

Thought process:
1. Build database from scratch by scraping local travel blogs, tourism websites, google and trip advisor to get recommendations / hidden gems about one location.
2. Machine train natural language processing (NLP) model
3. NLP model used to analyse the information/ text gathered via web scraping to get useful info like time to spend at a place and characteristic score of each location. Characteristic score allows us to know the whether the place is cultural, adventurous, romantic, nature etc. Each location will have a unique matrix of score.
4. Path planning using 'reinforced algorithm'. Path is planned by an agent whereby the goal of the agent is to maximise the reward for the user. Each user has slightly different reward (i.e. maximise budget, loves cultural places etc.)
5. Path planning takes into account of budget so the website will query for live flight and accommodation prices for consideration.
6. Web framework developed using Django and database host on AWS.
7. Minimum viable product focuses on Singapore first...
