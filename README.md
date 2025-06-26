# Financial Recommendation System

A recommendation system for financial transactions, offers, assets, and investment strategies.

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/dhruv230605/Recommendation-System-2.git
cd Recommendation-System-2
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the data:
   - Place your financial data JSON file in the `data` directory
   - Update the `DATA_PATH` in `backend/embeddings.py` to point to your data file

5. Generate FAISS indices:
```bash
python backend/embeddings.py
```

## Project Structure

- `backend/`: Contains the main application code
  - `embeddings.py`: Handles text embeddings and FAISS index generation
  - `chatbot.py`: Chatbot implementation
  - `data_manager.py`: Data management utilities
  - `analytics.py`: Analytics functionality
  - `auth.py`: Authentication system
  - `data_generator.py`: Data generation utilities
- `data/`: Directory for data files
- `faiss_multi_output/`: Generated FAISS indices and metadata

## Usage

After setup, you can:
1. Run the chatbot
2. Generate embeddings
3. Perform searches
4. Access analytics

## Requirements

- Python 3.11+
- Dependencies listed in requirements.txt
- Sufficient disk space for FAISS indices 