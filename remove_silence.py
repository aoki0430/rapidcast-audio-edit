import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


# 任意のフォーマットに変換
def convert_to_other_format(input_path, format):
    """
    input_path: 入力音声ファイルへのパス
    output_path: WAV形式の出力音声ファイルへのパス (デフォルトは "temp_converted.wav")
    """
    audio = AudioSegment.from_file(input_path, format=os.path.splitext(input_path)[1].replace(".", ""))
    output_path = os.path.splitext(input_path)[0] + "." + format
    audio.export(output_path, format=format)
    return output_path

def remove_silence_from_audio(input_path, output_path, silence_thresh=-50.0, min_silence_len=1000):
    """
    input_path: 入力オーディオファイルへのパス
    output_path: 出力オーディオファイルへのパス
    silence_thresh: 無音とみなす dB 以下の閾値
    min_silence_len: 無音として判定する最小ミリ秒
    """
    # TODO 扱うのはWAV形式のみにする

    if not input_path.endswith(".wav"):
        before_input_path = input_path
        input_path = convert_to_other_format(input_path, "wav")
        os.remove(before_input_path)

    audio = AudioSegment.from_wav(input_path)

    # オーディオから無音部分をカット
    chunks = split_on_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # カットした部分を結合
    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk

    # 出力ファイルに保存
    combined.export(output_path, format=os.path.splitext(output_path)[1].replace(".", ""))

    # 一時ファイルを削除
    os.remove(input_path)