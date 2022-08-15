import uvicorn


if __name__ == "__main__":
    uvicorn.run("bot_init:app", port=8000)
    