# StockPulse - AI Inventory & Dynamic Pricing Engine

StockPulse is an intelligent inventory management system with dynamic pricing capabilities powered by AI. It automatically generates pricing and reorder recommendations based on inventory levels, demand patterns, and market conditions.

## Project Structure

```
stockpulse/
├── backend/          # FastAPI backend with PostgreSQL
└── frontend/         # React + Vite frontend
```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=stockpulse
   DB_USER=postgres
   DB_PASSWORD=your_password
   GEMINI_API_KEY=your_gemini_api_key  # Optional
   ```

4. Start the backend server:
   ```bash
   python main.py
   ```

5. The backend will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (requires Node.js):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. The frontend will be available at `http://localhost:5173`

## Architecture

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Pydantic
- **AI Engine**: Google Gemini API (with rule-based fallback)
- **Frontend**: React + Vite
- **Communication**: REST API between frontend and backend

## Core Features

1. **Product Management**: CRUD operations for inventory items
2. **Order Simulation**: Place orders to reduce stock levels
3. **Stock Updates**: Manually adjust inventory levels
4. **Automatic Triggers**: 
   - Inventory-low triggers when stock < reorder threshold
   - Demand-spike triggers when demand velocity > 3x category average
5. **AI Recommendations**: 
   - Pricing suggestions based on inventory and demand
   - Reorder quantity recommendations
6. **Human Review**: Accept/reject AI-generated suggestions

## Demo Workflow

1. Start both backend and frontend servers
2. Open the dashboard at `http://localhost:5173`
3. View the 8 seeded products with their current status
4. **Inventory-Low Demo**:
   - Select PRD-003 (T-Shirt with stock=8, threshold=15)
   - Place an order for 8 units (stock becomes 0)
   - Observe automatic pricing and reorder suggestions
   - Accept/reject suggestions to update product data
5. **Demand-Spike Demo**:
   - Select PRD-008 (Hoodie)
   - Increase demand velocity to > 3x category average
   - Observe automatic suggestions being generated
6. Use the refresh button to see real-time updates

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.