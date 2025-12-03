Project Brief: Implementing the Codebase RAG System

## Project Overview

I am developing a **new Retrieval-Augmented Generation (RAG) system** for open-source codebases, **inspired by** the successful elements of my previous project (a local RAG setup for a 100+ hour Python course). The prior project enabled semantic search on video subtitles (SRT files) to retrieve ranked videos (e.g., "context managers" → relevant videos). It was straightforward due to organized content and proved the viability of key tools like LlamaIndex, LanceDB, Snowflake embeddings, ms-marco reranker, and a simple local setup (Streamlit/CLI).

This **new project** is **distinct in its goals, inputs, and outputs**:

- **Goals**: Bridge natural language learning outlines to actual code implementations in open-source repos, aiding developers/students in exploring concepts via real code (e.g., for React hooks or Django views).
- **Inputs**:
  - LLM-generated course outline topics (natural language, e.g., “Promises” in JavaScript).
  - Open-source codebase files (preprocessed embeddings).
- **Outputs**: Ranked code files/snippets implementing the concept (e.g., "Promises" → files like api.js or fetchData.js with relevant sections).
- **Key Shift**: From simple NL-to-NL transcript search to **NL-to-code mapping**, requiring embeddings strong enough to link abstract concepts to programming implementations across languages.
- **Core Components**:
  1. **Outline Generation**: Use an LLM (e.g., Grok) to create detailed but not overly granular course outlines for programming languages/frameworks.
  2. **Codebase Embedding and Retrieval**: Embed repo files (excluding irrelevant paths), semantically query with outline topics to retrieve top code matches.
- **Multi-Language Support**: Essential for spanning stacks (e.g., JS Promises vs. Python async), with easy DB updates for new projects/stacks.

This project is in early development (proof-of-concept stage), focusing on validating the core assumption: embedding models can accurately map NL concepts to code. The Blind Spot Navigator analysis (already completed) identified gaps and research questions, guiding prioritization.

## Objectives

- **Primary Goal**: Build a working POC within 1 week to test NL-to-code mapping accuracy, using components proven in the previous project where they fit.
- **Secondary Goals**:
  - Develop a standalone pipeline for outline generation + codebase search (not extending old scripts directly).
  - Handle preprocessing (ingestion, smart chunking for code) and ranking for relevance.
  - Incorporate GDR research findings (e.g., code-specific embeddings like VoyageCode3, chunking strategies).
  - Ensure adaptability for multi-language stacks without high costs.
- **Desired Outputs**: Functional scripts (e.g., new build_index.py, query.py), test results on small repos (e.g., Flask for Python), and a viability summary (e.g., "Mappings succeed for X but fail on Y").

## Main Concerns and Constraints

- **Technical Bottlenecks** (From Blind Spot Analysis):
  - Embedding model selection: Lightweight, code-optimized models (e.g., Nomic Embed Code) for local runs, or minimal Colab if needed.
  - Chunking and Preprocessing: Code-specific strategies (e.g., by functions/classes) to preserve context, differing from uniform SRT handling.
  - Semantic Mapping Accuracy: Queries like "Promises" retrieving implementations, using context (e.g., file extensions) to disambiguate languages.
  - Pipeline Integration and Testing: Low-confidence areas; quick POC validation on small repos.
  - GPU/Colab Workflow: If required, seamless input/output (e.g., save to Google Drive/bucket), under $10/month.
- **Feasibility Risks**:
  - Budget: Minimal (~$10/month for Colab Pro; previous was GPU-free, 20-30 min local).
  - Timeline: Max 1 week for POC—validate embedding viability as the key bottleneck.
  - Technical Capability: Intermediate/Advanced; solo developer.
  - Complexity: Keep simple; prefer open-source, plug-and-play with custom adaptations for new goals/IO.
- **Preferences**:
  - Build Upon Successes: Reuse LlamaIndex/LanceDB/etc. for robustness, but create fresh scripts tailored to new inputs/outputs.
  - Work Style: Mix—plug-and-play where possible, but not a direct extension (different nature requires tweaks).
  - Output Presentation: Mid-priority for POC (file paths OK; snippets/highlights later).

