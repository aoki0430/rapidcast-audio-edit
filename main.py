from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, auth, storage
import firebase_admin
from remove_silence import remove_silence_from_audio
import os

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/")
def Hello():
    return {"Hello":"World!"}

# Firebaseの初期化
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': "rapidcast.appspot.com"
})

bucket = storage.bucket()

@app.post("/edit_audio")
async def edit_audio(token: str, file_path: str):

    # token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImNmM2I1YWRhM2NhMzkxNTQ4ZDM1OTJiMzU5MjkyM2UzNjAxMmI5MTQiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiTi4gQW9raSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQWNIVHRkZ25qcTd5NWhhTENzYW1adDQ2WGZKWVFKOUF2bFpqLTBMQ25ZZUdDdnBvQm89czk2LWMiLCJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcmFwaWRjYXN0IiwiYXVkIjoicmFwaWRjYXN0IiwiYXV0aF90aW1lIjoxNjkxOTIyNDE5LCJ1c2VyX2lkIjoiMVlKUmpwbWRRUGFCZlRESmprZERSVVFqMFBQMiIsInN1YiI6IjFZSlJqcG1kUVBhQmZUREpqa2REUlVRajBQUDIiLCJpYXQiOjE2OTE5MjI0MTksImV4cCI6MTY5MTkyNjAxOSwiZW1haWwiOiJwYW5rdW4wNzE0QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTA5OTA0MzU2NDgyMDczNjA1MzkyIl0sImVtYWlsIjpbInBhbmt1bjA3MTRAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.PguY96s6ZWVqgAELVOqyrjy1BwKLEA8UNYxoiDvI7G3BrAC0a8loYuXnbm7-YE41sp3w08v7O3l5Dbnv6kdl_EOdTL26WLFiZXaJmCJRQA-5H-kBqcEo_A3NgvYNyPPSQIzU5BOKyhvYX45uzzyuNq4XQzM86lS0oJ7DMpRxAzb7CP46otHcodz-fDh-sIjNSKVfZDMyEObIXbM9TwcasZebEeggTQ_PcOoIRDfGs4Agp2yNIqfzKrTMaKdRbwF0L1ghhclaewGIzf8ZH4_mvQavwetDAE1LcdTv6mV0hB02OizGjoN1JRsDkaN-wwLT6YpZoJYH66xB7xDWVDDMow"
    # file_path = "user-audio-files/1YJRjpmdQPaBfTDJjkdDRUQj0PP2/output.mp3"
    
    # Firebase認証の確認
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    # 音声ファイルのダウンロード
    blob = bucket.blob(file_path)

    #file_pathの最後のスラッシュ以降をファイル名として取得
    input_path = file_path.split("/")[-1]
    blob.download_to_filename(input_path)
    format = input_path.split(".")[-1]

    # 音声を編集
    output_path = remove_silence_from_audio(input_path,f"edited_audio.{format}")

    # 編集済み音声のアップロード
    new_path = f"user-audio-files/{uid}/edited_audio.{format}"
    new_blob = bucket.blob(new_path)
    new_blob.upload_from_filename(output_path)

    # 一時ファイルの削除
    os.remove("temp_audio.wav")
    return {"edited_file_path": new_path}
