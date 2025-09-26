# L2_Newsletter_Publisher_v2.ipynb

## Overview

This notebook demonstrates a multi-agent workflow for assembling a machine-stable newsletter JSON from a set of news articles. It leverages CrewAI to orchestrate agents and tasks, using OpenAI's GPT-3.5-turbo as the LLM. The workflow includes reading, outlining, editorial writing, editing, and deterministic merging/saving of newsletter content.

## Workflow Steps

1. **Read and Outline**:  
    - The orchestrator agent reads a JSON file of news articles.
    - It selects the main article, derives 5 subtopics, and buckets articles per subtopic.

2. **Editorial Writing**:  
    - The writer agent drafts concise editorials for each subtopic and synthesizes a main editorial.

3. **Editing**:  
    - The editor agent refines the drafts for clarity, tone, and factual alignment.

4. **Merging and Saving**:  
    - The orchestrator agent deterministically merges the outline and edited copy into a final JSON.
    - The result is saved to disk using a custom `save_json` tool.

## Key Features

- **Deterministic Output**:  
  All merging and editorial steps follow strict, rule-based procedures to ensure reproducibility and machine-readability.

- **Agent Roles**:  
  - **Orchestrator**: Manages outline and final assembly.
  - **Writer**: Produces editorials.
  - **Editor**: Refines text for publication.


## Setup
- setup uv virtual environmnet 
- Create a .env in your current folder

``` txt
export OPENAI_API_KEY=<yourkey>
export OPENAI_MODEL_NAME=gpt-3.5-turbo
```
source .env

## Usage

Open the L2_Newsletter_Publisher_v2.ipynb in your vscode or some other notebook 
and then run all the cells after re-naming the existing newsletter.json file.

Then start modifying the file/*.md files and well as the crewAI tas/Tools prompts to see the difference in ourput

