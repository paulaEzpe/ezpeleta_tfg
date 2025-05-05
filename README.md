This project combines a React frontend, a python backend, and an OpenSearch engine, along with polarity and similarity analysis models.

🚀 Requirements
- Python 3.8 or higher
- Docker + Docker Compose
- Node.js and npm

🔧 Installation Instructions
1. Clone the repository
git clone https://github.com/paulaEzpe/ezpeleta_tfg.git
cd ezpeleta_tfg

2. Start OpenSearch (data)
From the opensearch/ directory:

cd opensearch
docker-compose up

This will start OpenSearch and (optionally) OpenSearch Dashboards.

3. Run the backend (python)
From the backend/ directory:

cd ../backend
pip install -r requirements.txt
python server.py

This will launch the backend and automatically load the models.
By default, it runs at: http://localhost:8000

4. Run the frontend
From the frontend/ directory:

cd ../frontend
npm install
npm start

This will open the app in your browser at: http://localhost:3000

✅ Additional Notes

- Make sure OpenSearch is running before starting the backend.
- The analysis models are automatically loaded from disk when running server.py
- Executing everything requires a lot of memory since loading all the models is pretty heavy at first
