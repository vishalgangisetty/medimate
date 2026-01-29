#  Medi-Mate

**Intelligent Prescription RAG Assistant with OTC Safety Verification**

Medi-Mate is an AI-powered healthcare assistant that helps users understand their medical prescriptions and verify the safety of over-the-counter (OTC) medicine purchases.

---

##  Features

###  Prescription Analysis
- **OCR & Extraction:** Upload handwritten or printed prescriptions (PDF/Image) and get structured data extraction using Google Gemini Vision.
- **Interactive Chat:** Ask questions about your prescription like *"When should I take this medicine?"* or *"What are the side effects?"*
- **Context Memory:** The AI remembers your conversation history for natural follow-up questions.

###  OTC Safety Checker
- **Vector-Powered Search:** Uses Pinecone semantic search to find medicine matches efficiently.
- **AI Verification:** LLM-based confirmation ensures accurate categorization.
- **Clear Results:** Medicines are classified as:
  -  **Safe to Buy** - Available OTC
  -  **Consult Doctor** - Requires professional advice

###  Medicine Reminder System 💊
- **Smart Scheduling:** Set reminders for daily, twice-daily, or thrice-daily medications
- **Adherence Tracking:** Track taken and missed doses with statistics
- **Flexible Timing:** Customize reminder times for each medicine
- **Food Instructions:** Mark medicines to be taken with/without food
- **Duration Management:** Set start date and duration for each medicine
- **📅 Google Calendar Integration:** Sync reminders to Google Calendar (optional)

### 🗺️ Pharmacy Locator
- **Search by Address:** Enter any address or location name (e.g., "Connaught Place, Delhi")
- **Search by Coordinates:** Use GPS coordinates for precise location search
- **Find Nearby Pharmacies:** Powered by Google Places API
- **Contact Information:** Get phone numbers and addresses
- **Real-time Status:** See if pharmacies are currently open
- **Directions:** Get Google Maps directions to any pharmacy
- **Ratings & Reviews:** View ratings and user reviews
- **Flexible Radius:** Search from 1-50 km radius

### 🌍 Multi-Language Support
- **10 Indian Languages:** English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi
- **Dynamic Translation:** UI elements translate in real-time
- **Prescription Translation:** Translate prescription data to your preferred language
- **Easy Switching:** Change language anytime from the sidebar

###  User Management
- Secure login/registration with bcrypt password hashing.
- Per-user prescription history and chat sessions.
- Persistent data storage in MongoDB.
---

##  Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  LangGraph RAG   │────▶│  Google Gemini  │
│   (Frontend)    │     │   (Orchestrate)  │     │     (LLM)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│    MongoDB      │     │    Pinecone      │
│ (Auth, History) │     │ (Vector Search)  │
└─────────────────┘     └──────────────────┘
```

---

##  Project Structure

```
medi-mate-0.1/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not tracked)
│
├── src/
│   ├── auth.py            # User authentication (MongoDB + bcrypt)
│   ├── config.py          # Configuration & environment loading
│   ├── extractor.py       # Prescription OCR using Gemini Vision
│   ├── graph.py           # LangGraph RAG pipeline
│   ├── ingestion.py       # File processing utilities
│   ├── memory.py          # Chat history & session management
│   ├── otc_data.py        # OTC medicines list (structured data)
│   ├── otc_manager.py     # OTC verification engine
│   ├── utils.py           # Helper functions & logging
│   └── vector_store.py    # Pinecone vector database interface
│
├── data/
│   ├── input/             # Uploaded prescription files
│   └── processed/         # Processed outputs
│
└── tests/
    └── test_otc_check.py  # OTC verification tests
```

---

##  Getting Started

### Prerequisites
- Python 3.10+
- MongoDB Atlas account (or local MongoDB)
- Pinecone account
- Google Cloud account (Gemini API) (prefer gemini 2.5 flash lite, cheapest and fastest model out there with good accuracy )
- if you want run locally i prefer gemma 3 4 billion model using ollama.

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd medi-mate-0.1
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/medi-mate
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

##  Configuration

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key for LLM and Vision. Also used for Google Places API (Pharmacy Locator) - **Enable Places API in Google Cloud Console** |
| `PINECONE_API_KEY` | Pinecone API key for vector database |
| `MONGO_URI` | MongoDB connection string |

**Optional Features:**
- **Google Calendar Integration:** See [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md) for setup
- **Google Places API:** Enable in Google Cloud Console for pharmacy locator feature

---

##  Usage

### Upload a Prescription
1. Login or create an account.
2. Use the file uploader in the sidebar to upload a prescription (PDF, PNG, JPG).
3. The system will extract medicine details automatically.

### Chat with Your Prescription
- Ask questions like:
  - *"What is the dosage for the first medicine?"*
  - *"Are there any food restrictions?"*
  - *"Explain the timing instructions."*

### Check OTC Safety
1. Click the **"Check for OTC Medicines"** checkbox.
2. View results categorized as Safe or Consult.
3. Navigate to the **OTC List** page to browse all allowed medicines.

### Set Medicine Reminders
1. Navigate to **Medicine Reminders** from the sidebar.
2. Fill in medicine details, dosage, and timing.
3. (Optional) Check **"Add to Google Calendar"** for automatic calendar sync.
4. View today's schedule and mark doses as taken.
5. Track your adherence statistics.

**For Google Calendar Setup:** See [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md)

### Find Nearby Pharmacies
1. Go to **Pharmacy Locator** from the sidebar.
2. **By Address Tab:** Enter your location (e.g., "Connaught Place, Delhi")
3. **By Coordinates Tab:** Enter GPS coordinates
4. Set search radius and click Search.
5. View pharmacies with phone numbers, ratings, and directions.

### Change Language
1. Use the language selector in the sidebar.
2. Choose from 10 Indian languages.
3. UI will update instantly.

---

##  Testing

Run OTC verification tests:
```bash
python -m pytest tests/test_otc_check.py -v
```

---

##  Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **LLM / AI** | Google Gemini (Flash Lite) |
| **Vector DB** | Pinecone |
| **Database** | MongoDB |
| **Orchestration** | LangChain, LangGraph |
| **Auth** | bcrypt |

---

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

##  Disclaimer

**Medi-Mate is not a substitute for professional medical advice.** Always consult a qualified healthcare provider for medical decisions. The OTC classification is based on general guidelines and may not apply to all regions or individual health conditions.

---
