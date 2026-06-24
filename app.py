import time
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI()

# ---------------------------------------------------
# 1. Déclaration des métriques Prometheus
# ---------------------------------------------------

api_requests_total = Counter(
    "api_requests_total",
    "Nombre total de requêtes HTTP",
    ["method", "endpoint", "status_code"]
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "Durée des requêtes HTTP",
    ["method", "endpoint"]
)

# ---------------------------------------------------
# 2. Middleware pour mesurer chaque requête
# ---------------------------------------------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    # Mise à jour des métriques
    api_requests_total.labels(method, endpoint, status_code).inc()
    api_request_duration_seconds.labels(method, endpoint).observe(duration)

    return response

# ---------------------------------------------------
# 3. Routes API
# ---------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API FastAPI + Prometheus !"}

@app.get("/traitement")
async def traitement():
    time.sleep(0.2)  # simulation d'un traitement
    return {"message": "Traitement terminé !"}

# ---------------------------------------------------
# 4. Exposition du endpoint /metrics via ASGI
# ---------------------------------------------------

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# ---------------------------------------------------
# 5. Lancement uvicorn :
uvicorn app:app --host 0.0.0.0 --port 5001 --reload
# ---------------------------------------------------
