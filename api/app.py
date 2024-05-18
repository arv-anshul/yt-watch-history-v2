from fastapi import FastAPI

from src import routes

app = FastAPI()


@app.get("/")
async def root():
    return {
        "author": {
            "github": "https://github.com/arv-anshul/",
            "linkedin": "https://linkedin.com/in/arv-anshul/",
        },
        "message": "🙏 Namaste!",
    }


app.include_router(
    routes.youtube.video.router,
    prefix="/yt/video",
    tags=["video"],
)
app.include_router(
    routes.db.youtube.video.router,
    prefix="/db/yt/video",
    tags=["video"],
)
app.include_router(
    routes.db.youtube.channel_video.router,
    prefix="/db/yt/channel/video",
    tags=["channel", "channelVideo"],
)
