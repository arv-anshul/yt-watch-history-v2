# YouTube Watch History Analyser - V2

Analyse you YouTube Watch History using Machine Learning, plot graphs, etc.

<p align="center">
<a href="https://github.com/arv-anshul/yt-watch-history"><img src="https://img.shields.io/badge/Project%20V1-181717?logo=github&amp;logoColor=fff" alt="GitHub"></a>
<a href="https://arv-anshul.github.io/project/yt-watch-history"><img src="https://img.shields.io/badge/Project%20Webpage-526CFE?logo=materialformkdocs&amp;logoColor=fff" alt="Material for MkDocs"></a>
<a href="https://arv-anshul.github.io/project/yt-watch-history/v2-architecture"><img src="https://img.shields.io/badge/Project%20Architecture%20Diagram-FF3670?logo=mermaid&amp;logoColor=fff" alt="Mermaid"></a>
</p>

<p align=center>
  <img src="assets/img/diagram-for-v2.png" height="450px" title="Architecture of Project">
</p>

## Working

### API (Backend)

- Used FastAPI to create backend APIs to interact with **MongoDB** database.
- Used **YouTube Data API v3** to fetch details about videos (you have watched).
- Used **Docker** to containerize the FastAPI application.

### ML (Models and API)

**Models**

1. **Video's Content Type Predictor**
   - Multiclass Classification Problem
   - Uses _Video Title_ to predict Content Type
2. **Channel Recommender System**
   - Recommender System
   - Uses channel's videos title and tags to calculate similarity
   - Uses `TfidfVectorizer` for text to vec convertion
   - Uses user's channel subscriptions data to recommend channel

> \[!IMPORTANT\]
>
> By the way, I'm planning to upload the trained model to internet and model is download from URL to docker container
> once (if not exists).
>
> The model URL is provide through environment variable (`CTT_MODEL_URL`). If you want you can provide your model's URL.
>
> _This solution may works in short term_ 🤞

**API**

- Used **FastAPI** to serve model.
- Containerize FastAPI application and models using **Docker**.

### Frontend

- Uses **Streamlit** to create multipage web application where users can upload their required data and see analysis.
- Requires **YouTube API Key** to fetch video details from API for advance analysis.
- Uses **httpx** library to interact make requests to "Backend APIs" and "ML APIs".
- Uses **Polars** for data manipulation.

### Apps Composition

- Wrote [docker-compose.yaml] script to build and run all three containers in one go.
- Used `mongodb` docker image as database, see [docker-compose.yaml].

## Setup

Clone this GitHub Repository

```bash
git clone https://github.com/arv-anshul/yt-watch-history-v2
cd yt-watch-history-v2
```

Train ML model [CTT model](ml/src/ctt/training.py) using below command:

```bash
cd ./ml
```

```bash
# Using rye
rye run python -m src.ctt.model

# Using python (activate virtual environment)
python -m src.ctt.model
```

Open **Docker Desktop** and run below command:

👀 See [docker-compose.yaml]

```bash
docker compose up --build  # First build the container and then run it (for first time)
```

## Roadmap

- [x] 🛠️ Build the basics from [yt-watch-history] project
- [x] 🎨 Draw diagrams for references
- [x] ⛓️ How to intergrate **pre-trained** ML Model
- [x] 🤖 Build **Channel Recommender System**
- [ ] 👷 Better CTT Model pipeline
- [ ] 📌 Integrate `mlflow` for ML Model monitoring

[docker-compose.yaml]: docker-compose.yaml
[yt-watch-history]: https://github.com/arv-anshul/yt-watch-history
