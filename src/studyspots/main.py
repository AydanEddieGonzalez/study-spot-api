from fastapi import FastAPI

app = FastAPI(title='Study Spot API')


@app.get('/health')
def health():
    return {'status': 'ok'}

