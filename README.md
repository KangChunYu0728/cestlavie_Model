# Salad Plant Growth Analysis API

## Overview
This project uses the OpenAI API to process natural language queries related to the growth of salad plants. Users can submit prompts, and the system will retrieve relevant data, perform analysis, and generate insights in the form of text or analytical graphs.

## Workflow
### 1. User Query Processing
- Users submit a prompt (e.g., *"Show me the weight trend of Iceberg lettuce over the last 3 months."*).
- The API receives and forwards the request to OpenAI for processing.

### 2. Natural Language Processing (NLP) with OpenAI API
- OpenAI interprets the query to determine:
  - The **type of request** (data retrieval, statistical summary, graph generation).
  - The **parameters** (salad type, time range, growth metrics such as height or weight).
- The system identifies the best visualization type if a graph is required.

### 3. Database Query Execution
- The backend translates the extracted parameters into a **SQL or NoSQL query**.
- The database fetches the relevant **growth data** (height, weight, volume, etc.).

### 4. Data Processing & Analysis
- Data is cleaned and prepared for analysis.
- If necessary, statistical computations (e.g., averages, growth rates) are performed.

### 5. Visualization & Response Generation
- If a graph is needed:
  - Data is plotted using **Matplotlib/Plotly**.
  - The graph is saved and returned as an image link.
- If a text response is needed:
  - A summary is generated based on the data.
  - OpenAI refines the response into a user-friendly format.

### 6. API Response & User Output
- The API returns either:
  - A **graph image** (if visualization was requested).
  - A **text-based analytical insight** (if no visualization was needed).
- The frontend displays the result to the user.

## Technology Stack
| Component              | Tool/Technology           |
|------------------------|--------------------------|
| **Backend API**       | FastAPI / Flask          |
| **Database**          | MySQL / PostgreSQL / MongoDB |
| **AI Model**          | OpenAI GPT-4 (via API)   |
| **Visualization**     | Matplotlib / Seaborn / Plotly |
| **Deployment**        | Docker + Cloud (AWS/GCP) |

## Setup Instructions
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/salad-growth-api.git
   cd salad-growth-api
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables for OpenAI API key and database connection.
4. Run the backend API:
   ```sh
   python main.py
   ```
5. Test API endpoints using Postman or a web client.


