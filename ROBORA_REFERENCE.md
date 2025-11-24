# RoboRA Project Reference

## Executive Summary

**RoboRA** (Robotic Research Assistant) is a Python library designed to automate the process of gathering structured information using Large Language Models (LLMs), specifically Perplexity's Sonar models. It enables researchers to define complex sets of questions using templates, execute these queries against an AI API, and store the structured results for analysis.

The system acts as a force multiplier for research tasks, allowing a user to convert a single research intent (e.g., "Find the GDP of these 50 countries") into a robust, automated workflow that handles API communication, error handling, caching, and data persistence.

## Background & Purpose

Research often involves repetitive information gathering tasks where the same type of question is asked across multiple subjects (e.g., companies, countries, products). Manual search is time-consuming and inconsistent.

The purpose of RoboRA is to:
1.  **Automate Data Collection**: Replace manual web searches with automated AI queries.
2.  **Ensure Structure**: Force the AI to return data in a specific JSON format (defined by Pydantic models) rather than unstructured text.
3.  **Persist & Cache**: Save results to a local database to prevent redundant API calls and allow for longitudinal analysis.
4.  **Verify Sources**: Leverage the Sonar model's citation capabilities to provide source URLs for every data point.

## Solution

RoboRA provides a modular architecture to solve the research automation problem:

### Core Components

*   **`Question` & `QuestionSet`**:
    *   Allows users to define a **Template** (e.g., "What is the {metric} for {entity}?").
    *   Users provide **Word Sets** (lists of variables).
    *   The system automatically generates the Cartesian product of all variables to create a list of unique questions.

*   **`SonarQueryHandler`**:
    *   Interfaces with the Perplexity Sonar API.
    *   Injects the target JSON schema into the prompt to ensure the AI response matches the expected format.
    *   Enriches the response with "pretty citations," linking facts to their source URLs.

*   **`SQLiteStorageProvider`**:
    *   A persistent storage layer backed by SQLite.
    *   Hashes questions to create unique IDs.
    *   Caches responses: If a question has already been answered in the database, the system skips the API call, saving time and money.

*   **`Workflow`**:
    *   The orchestration engine that ties everything together.
    *   Manages concurrency (async/await) to process multiple questions in parallel.
    *   Handles the logic of "Check Cache -> Query API -> Save Result".

## Methodology

A typical research workflow using RoboRA follows these steps:

1.  **Define the Data Model**:
    Create a Pydantic model representing the data you want to extract.
    ```python
    class CountryStats(BaseModel):
        gdp: float
        population: int
        currency: str
    ```

2.  **Construct the Question Set**:
    Define the template and the variables.
    ```python
    qs = QuestionSet(
        template="Get the statistics for {country}",
        word_sets={"country": ["France", "Germany", "Japan"]},
        response_model=CountryStats
    )
    ```

3.  **Initialize the Workflow**:
    Set up the storage and query handler.
    ```python
    storage = SQLiteStorageProvider("research.db")
    handler = SonarQueryHandler(response_model=CountryStats)
    workflow = Workflow(query_handler=handler, storage=storage)
    ```

4.  **Execute**:
    Run the workflow. The system will process the questions, hitting the API only for new questions.
    ```python
    answers = await workflow.ask_multiple(qs)
    ```

5.  **Analyze**:
    Convert the results into a Pandas DataFrame for analysis.
    ```python
    df = pd.DataFrame([a.flattened for a in answers])
    ```

## Barriers & Limitations

*   **API Dependency**: The system relies heavily on the Perplexity API. Rate limits, API costs, and service downtime are external dependencies that can affect the workflow.
*   **Model Accuracy**: While Sonar is designed for search, it can still hallucinate or retrieve outdated information. The citation feature mitigates this but does not eliminate it.
*   **Schema Rigidity**: The system requires the AI to output valid JSON according to a strict schema. If the model fails to conform (despite the prompt instructions), the query may fail or require retries.
*   **Context Window**: Extremely complex questions or very large schemas might exceed the context window of the underlying model.
*   **Storage**: Currently, the primary persistent storage is SQLite. While sufficient for most individual research projects, it may not scale to massive, distributed scraping operations without migration to a more robust database server.
