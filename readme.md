# AI Travel Planner

The **AI Travel Planner** is a multi-agent application that automatically plans complete travel itineraries, including flights, hotels, and tourist attractions, using real-time data from the Booking.com API (via RapidAPI). It uses LangChain and LangGraph for orchestration, Google’s Gemini model for reasoning, and Streamlit for the user interface.

## Demo

You can try a live demo of the project here:  
**[👉 Demo](https://huggingface.co/spaces/sameerrawat07/travelAgent)**

---

## Overview

This project demonstrates how large language models can coordinate multiple specialized agents to perform complex, real-world tasks. It uses three main agents:
- **Flight Agent** – Fetches flight details between two locations.
- **Hotel Agent** – Retrieves hotel options for the destination city.
- **Tourist Agent** – Finds tourist attractions and activities.

A **Supervisor Agent** manages these three agents and combines their outputs into two curated travel packages:
1. **Economical Package** – Budget-friendly trip with economical flights, affordable hotels, and free or low-cost attractions.
2. **Luxurious Package** – Premium trip with business-class flights, luxury hotels, and exclusive attractions.

---

## Key Features

- Uses real data from Booking.com APIs via RapidAPI.
- Multi-agent coordination using LangGraph and LangChain.
- Observability and tracing with LangSmith.
- Streamlit-based front end for easy interaction.
