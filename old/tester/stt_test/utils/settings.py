# GPU 사용 여부 전역 변수 (초기 상태: False)
USE_GPU = False

def toggle_gpu():
    global USE_GPU
    USE_GPU = not USE_GPU
    return USE_GPU
