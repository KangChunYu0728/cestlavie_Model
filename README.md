# Salad Plant Growth Analysis System

## Overview
This system leverages the **Ollama** open-source model for analyzing plant growth data. It allows users to input queries about plant growth and receive textual insights as well as graphical visualizations (e.g., growth trends, predictions) directly in **Power Apps**. The system utilizes **Microsoft Dataverse** for data storage and **Azure** for model hosting and API deployment.

## Workflow

1. **Data Management:**
   - Data is updated weekly in **Microsoft List** and migrated to **Microsoft Dataverse** using **Power Automate**.

2. **Model Development:**
   - The **Ollama model** is used to generate insights and predictions based on plant growth data.
   - Here is the repo for Ollama: https://github.com/ollama/ollama
   - Graphs are generated using **Matplotlib** or **Plotly**.

3. **API Deployment:**
   - The model is deployed as an API on **Azure App Service** or **Azure Functions**.
   - The API handles user queries, processes them with the Ollama model, and returns textual insights and graphs.

4. **Frontend (Power Apps):**
   - **Power Apps** serves as the user interface, where users input queries and view results (textual insights and graphs).
   - **Power Automate** integrates Power Apps with the Azure-hosted model API.

## Steps to Deploy

1. **Set up Microsoft Dataverse** for storing plant data.
2. **Migrate plant data** from Microsoft List to Dataverse using Power Automate.
3. **Train and deploy the Ollama model** on Azure (using FastAPI or Flask).
4. **Integrate the model API** with Power Apps using Power Automate.
5. **Test the system** to ensure smooth user interaction and real-time graph generation.

## Prerequisites

- **Microsoft Dataverse** for data storage.
- **Azure Subscription** for deploying the model and API.
- **Power Apps** for the frontend user interface.
- **Power Automate** for workflow automation.
- **Matplotlib/Plotly** for generating graphs.
- **Ollama model** for plant growth analysis.

## Workflow

<img width="912" alt="Screenshot 2025-03-01 at 10 12 16 PM" src="https://github.com/user-attachments/assets/aa8a6562-46f6-4b88-9e93-25a58f86fe10" />

