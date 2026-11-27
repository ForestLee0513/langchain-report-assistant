from sqlalchemy import text
import torch

from app.core.db import db


def db_preflight():
    """GPU 가속가능 여부를 확인합니다.
    
    Apple MPS도 지원 범위에 포함합니다.
    
    Return: Boolean  
    Exception: RuntimeError"""
    try:
        with db.connect() as transction:
            transction.execute(text("SELECT 1"))

        return True
    except:
        raise RuntimeError("ERROR: DB is cannot be initialized. please check a config")


def gpu_preflight():
    """GPU 가속가능 여부를 확인합니다.
    
    Apple MPS도 지원 범위에 포함합니다.
    
    Return: 선택된 GPU의 하드웨어 정보  
    Exception: RuntimeError"""
    try:
        # CUDA
        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            return {
                "type": "cuda",
                "device": torch.device(f"cuda:{idx}"),
                "name": torch.cuda.get_device_name(idx),
                "count": torch.cuda.device_count(),
            }

        # Apple MPS
        if torch.mps.is_available():
            return {
                "type": "mps",
                "device": torch.device("mps"),
                "name": "Apple Silicon GPU (MPS)",
                "count": 1,
            }
    except:
        raise RuntimeError("ERROR: GPU acceleration is cannot be initialized. please check a hardware or driver config")
