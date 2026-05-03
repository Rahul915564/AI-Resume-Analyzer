# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.
Also contains a standalone Python Streamlit app at the workspace root.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Python Streamlit App

- **Entry point**: `app.py` (root)
- **Framework**: Streamlit 1.57+
- **AI**: Google Gemini 1.5 Flash via `google-generativeai`
- **PDF parsing**: PyPDF2
- **Charts**: Plotly
- **PDF export**: fpdf2
- **Config**: `.streamlit/config.toml` (port 5000)
- **Secrets**: `GEMINI_API_KEY` (Replit secret)
- **Workflow**: `Start application` — `streamlit run app.py --server.port 5000`

### Features
- PDF resume upload and text extraction
- Job description input
- Gemini AI analysis: ATS score, skills match, missing keywords, strengths/weaknesses, suggestions, rewritten summary
- Visualizations: gauge chart, radar chart, horizontal bar chart
- Hindi / English language toggle
- Download analysis as PDF report

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
