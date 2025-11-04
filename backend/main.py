from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import os
import shutil
import uuid
from dotenv import load_dotenv

from stego.analyzer import analyze_image
from stego.ai_adapter import get_grok_recommendation
from stego.lsb_encoder import encode_lsb
from stego.lsb_decoder import decode_lsb
from stego.audio_wav_encoder import encode_audio_lsb
from stego.audio_wav_decoder import decode_audio_lsb
from stego.video_encoder import encode_video_lsb
from stego.video_decoder import decode_video_lsb
from stego.dct_encoder import encode_dct
from stego.dct_decoder import decode_dct
from stego.dwt_encoder import encode_dwt
from stego.dwt_decoder import decode_dwt
from stego.crypto import encrypt_payload, decrypt_payload
from stego.metrics import calculate_metrics, calculate_audio_metrics, calculate_video_metrics
from stego.ai_explainer import get_explainer
from stego.ai_steganalysis import get_detector
from stego.ai_report_generator import get_report_generator

load_dotenv()

app = FastAPI(title="SteganoGen API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "SteganoGen API is running", "version": "1.0.0"}


@app.post("/api/analyze")
async def analyze(
    carrier: UploadFile = File(...),
    payload_text: Optional[str] = Form(None),
    goal: str = Form("max_invisibility")
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier image provided")
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format: {file_ext}. Supported: PNG, JPG, BMP, TIFF"
            )
        
        if goal not in ["max_invisibility", "max_capacity", "balanced"]:
            goal = "max_invisibility"
        
        file_id = str(uuid.uuid4())
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            if len(content) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image too large. Maximum: 50MB")
            buffer.write(content)
        
        image_stats = analyze_image(carrier_path)
        
        payload_size = len(payload_text.encode('utf-8')) if payload_text else 100
        
        if payload_size > image_stats.get('max_capacity_bytes', 0):
            raise HTTPException(
                status_code=400,
                detail=f"Payload too large. Need {payload_size} bytes, image capacity: {image_stats.get('max_capacity_bytes', 0)} bytes at 1 bit/channel"
            )
        
        recommendation = get_grok_recommendation(image_stats, payload_size, goal)
        
        return {
            "success": True,
            "file_id": file_id,
            "carrier_path": carrier_path,
            "image_stats": image_stats,
            "recommendation": recommendation,
            "payload_size": payload_size
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"Analysis error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/encode")
async def encode(
    carrier: UploadFile = File(...),
    payload_text: Optional[str] = Form(None),
    payload_file: Optional[UploadFile] = File(None),
    encryption_key: Optional[str] = Form(None),
    bits_per_channel: int = Form(1),
    file_id: Optional[str] = Form(None)
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier image provided")
        
        if not payload_text and not payload_file:
            raise HTTPException(status_code=400, detail="Either payload_text or payload_file must be provided")
        
        if bits_per_channel < 1 or bits_per_channel > 4:
            raise HTTPException(
                status_code=400,
                detail=f"bits_per_channel must be between 1 and 4, got {bits_per_channel}"
            )
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format: {file_ext}. Supported: PNG, JPG, BMP, TIFF"
            )
        
        if not file_id:
            file_id = str(uuid.uuid4())
        
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            if len(content) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image too large. Maximum: 50MB")
            buffer.write(content)
        
        if payload_file:
            payload_bytes = await payload_file.read()
            if len(payload_bytes) == 0:
                raise HTTPException(status_code=400, detail="Empty payload file")
            if len(payload_bytes) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Payload file too large. Maximum: 10MB")
        else:
            if len(payload_text) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Payload text too large. Maximum: 10MB")
            payload_bytes = payload_text.encode('utf-8')
        
        metadata = {}
        if encryption_key:
            try:
                encrypted = encrypt_payload(payload_bytes, encryption_key)
                payload_bytes = encrypted['encrypted_data']
                metadata['iv'] = encrypted['iv'].hex()
                metadata['encrypted'] = True
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Encryption failed: {str(ve)}")
        else:
            metadata['encrypted'] = False
        
        metadata_str = f"STEGANO|{metadata['encrypted']}|{metadata.get('iv', '')}|"
        full_payload = metadata_str.encode('utf-8') + payload_bytes
        
        output_filename = f"{file_id}_stego.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            encode_result = encode_lsb(carrier_path, full_payload, output_path, bits_per_channel)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        try:
            metrics = calculate_metrics(carrier_path, output_path)
        except Exception as me:
            print(f"Warning: Metrics calculation failed: {me}")
            metrics = {"psnr": 0, "ssim": 0, "mse": 0}
        
        return {
            "success": True,
            "file_id": file_id,
            "output_filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "encode_info": encode_result,
            "metrics": metrics
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"Encoding error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    finally:
        if carrier_path and os.path.exists(carrier_path) and not file_id:
            try:
                os.remove(carrier_path)
            except:
                pass


@app.post("/api/decode")
async def decode(
    stego_image: UploadFile = File(...),
    decryption_key: Optional[str] = Form(None),
    bits_per_channel: int = Form(1)
):
    stego_path = None
    try:
        if bits_per_channel < 1 or bits_per_channel > 4:
            raise HTTPException(
                status_code=400, 
                detail=f"bits_per_channel must be between 1 and 4, got {bits_per_channel}"
            )
        
        if not stego_image.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(stego_image.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Use PNG for best results."
            )
        
        file_id = str(uuid.uuid4())
        stego_path = os.path.join(UPLOAD_DIR, f"{file_id}_stego_{stego_image.filename}")
        
        with open(stego_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        
        extracted_bytes = decode_lsb(stego_path, bits_per_channel)
        
        is_encrypted = False
        metadata_str = extracted_bytes.split(b'|', 3)
        
        if len(metadata_str) >= 4 and metadata_str[0] == b'STEGANO':
            is_encrypted = metadata_str[1] == b'True'
            iv_hex = metadata_str[2].decode('utf-8')
            payload_bytes = metadata_str[3]
            
            if is_encrypted:
                if not decryption_key:
                    raise HTTPException(
                        status_code=400, 
                        detail="This message is encrypted. Decryption key is required."
                    )
                
                try:
                    iv = bytes.fromhex(iv_hex)
                    payload_bytes = decrypt_payload(payload_bytes, iv, decryption_key)
                except ValueError as ve:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decryption failed: {str(ve)}"
                    )
        else:
            payload_bytes = extracted_bytes
            is_encrypted = False
        
        payload_text = None
        is_binary = False
        try:
            payload_text = payload_bytes.decode('utf-8')
        except UnicodeDecodeError:
            is_binary = True
            payload_text = f"Binary data ({len(payload_bytes)} bytes)"
        
        return {
            "success": True,
            "payload": payload_text,
            "payload_size": len(payload_bytes),
            "was_encrypted": is_encrypted,
            "is_binary": is_binary,
            "payload_base64": payload_bytes.hex() if is_binary else None
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")
    finally:
        if stego_path and os.path.exists(stego_path):
            try:
                os.remove(stego_path)
            except:
                pass


@app.get("/api/download/{filename}")
async def download(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_ext = os.path.splitext(filename)[1].lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska'
    }
    media_type = media_type_map.get(file_ext, 'application/octet-stream')
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


@app.post("/api/encode/audio")
async def encode_audio(
    carrier: UploadFile = File(...),
    payload_text: str = Form(...),
    encryption_key: Optional[str] = Form(None),
    bits_per_sample: int = Form(2)
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier audio provided")
        
        if not payload_text:
            raise HTTPException(status_code=400, detail="No payload text provided")
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.wav']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {file_ext}. Only WAV is supported."
            )
        
        if bits_per_sample < 1 or bits_per_sample > 4:
            raise HTTPException(
                status_code=400,
                detail=f"bits_per_sample must be between 1 and 4, got {bits_per_sample}"
            )
        
        file_id = str(uuid.uuid4())
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            buffer.write(content)
        
        payload_bytes = payload_text.encode('utf-8')
        
        metadata = {}
        if encryption_key:
            try:
                encrypted = encrypt_payload(payload_bytes, encryption_key)
                payload_bytes = encrypted['encrypted_data']
                metadata['iv'] = encrypted['iv'].hex()
                metadata['encrypted'] = True
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Encryption failed: {str(ve)}")
        else:
            metadata['encrypted'] = False
        
        metadata_str = f"STEGANO|{metadata['encrypted']}|{metadata.get('iv', '')}|"
        full_payload = metadata_str.encode('utf-8') + payload_bytes
        
        output_filename = f"{file_id}_stego.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            encode_result = encode_audio_lsb(carrier_path, full_payload, output_path, bits_per_sample)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        try:
            metrics = calculate_audio_metrics(carrier_path, output_path)
        except Exception as me:
            print(f"Warning: Audio metrics calculation failed: {me}")
            metrics = {"snr": 0, "quality": "Unknown", "description": "Metrics unavailable"}
        
        return {
            "success": True,
            "file_id": file_id,
            "output_filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "encode_info": encode_result,
            "metrics": metrics
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"Audio encoding error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Audio encoding failed: {str(e)}")
    finally:
        if carrier_path and os.path.exists(carrier_path):
            try:
                os.remove(carrier_path)
            except:
                pass


@app.post("/api/decode/audio")
async def decode_audio(
    stego_audio: UploadFile = File(...),
    decryption_key: Optional[str] = Form(None),
    bits_per_sample: int = Form(2)
):
    stego_path = None
    try:
        if bits_per_sample < 1 or bits_per_sample > 4:
            raise HTTPException(
                status_code=400,
                detail=f"bits_per_sample must be between 1 and 4, got {bits_per_sample}"
            )
        
        if not stego_audio.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(stego_audio.filename)[1].lower()
        if file_ext not in ['.wav']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Only WAV is supported."
            )
        
        file_id = str(uuid.uuid4())
        stego_path = os.path.join(UPLOAD_DIR, f"{file_id}_stego_{stego_audio.filename}")
        
        with open(stego_path, "wb") as buffer:
            shutil.copyfileobj(stego_audio.file, buffer)
        
        extracted_bytes = decode_audio_lsb(stego_path, bits_per_sample)
        
        is_encrypted = False
        metadata_str = extracted_bytes.split(b'|', 3)
        
        if len(metadata_str) >= 4 and metadata_str[0] == b'STEGANO':
            is_encrypted = metadata_str[1] == b'True'
            iv_hex = metadata_str[2].decode('utf-8')
            payload_bytes = metadata_str[3]
            
            if is_encrypted:
                if not decryption_key:
                    raise HTTPException(
                        status_code=400,
                        detail="This message is encrypted. Decryption key is required."
                    )
                
                try:
                    iv = bytes.fromhex(iv_hex)
                    payload_bytes = decrypt_payload(payload_bytes, iv, decryption_key)
                except ValueError as ve:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decryption failed: {str(ve)}"
                    )
        else:
            payload_bytes = extracted_bytes
            is_encrypted = False
        
        try:
            payload_text = payload_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Could not decode payload as text. Wrong parameters or corrupted data."
            )
        
        return {
            "success": True,
            "payload": payload_text,
            "payload_size": len(payload_bytes),
            "was_encrypted": is_encrypted
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio decoding failed: {str(e)}")
    finally:
        if stego_path and os.path.exists(stego_path):
            try:
                os.remove(stego_path)
            except:
                pass


@app.post("/api/encode/video")
async def encode_video_endpoint(
    carrier: UploadFile = File(...),
    payload_text: Optional[str] = Form(None),
    payload_file: Optional[UploadFile] = File(None),
    encryption_key: Optional[str] = Form(None),
    bits_per_channel: int = Form(1),
    frame_skip: int = Form(1)
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier video provided")
        
        if not payload_text and not payload_file:
            raise HTTPException(status_code=400, detail="Either payload_text or payload_file must be provided")
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.mp4', '.avi', '.mov', '.mkv']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video format: {file_ext}. Supported: MP4, AVI, MOV, MKV"
            )
        
        if bits_per_channel < 1 or bits_per_channel > 4:
            raise HTTPException(
                status_code=400,
                detail=f"bits_per_channel must be between 1 and 4, got {bits_per_channel}"
            )
        
        if frame_skip < 1:
            raise HTTPException(status_code=400, detail="frame_skip must be at least 1")
        
        file_id = str(uuid.uuid4())
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            buffer.write(content)
        
        # Handle text or binary file payload
        if payload_file:
            payload_bytes = await payload_file.read()
            if len(payload_bytes) == 0:
                raise HTTPException(status_code=400, detail="Empty payload file")
        else:
            payload_bytes = payload_text.encode('utf-8')
        
        metadata = {}
        if encryption_key:
            try:
                encrypted = encrypt_payload(payload_bytes, encryption_key)
                payload_bytes = encrypted['encrypted_data']
                metadata['iv'] = encrypted['iv'].hex()
                metadata['encrypted'] = True
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Encryption failed: {str(ve)}")
        else:
            metadata['encrypted'] = False
        
        metadata_str = f"STEGANO|{metadata['encrypted']}|{metadata.get('iv', '')}|"
        full_payload = metadata_str.encode('utf-8') + payload_bytes
        
        output_filename = f"{file_id}_stego.avi"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            encode_result = encode_video_lsb(
                carrier_path, 
                full_payload, 
                output_path, 
                bits_per_channel, 
                frame_skip,
                use_uncompressed=True,  # Use lossless codec to preserve LSB data
                store_params=True       # Store parameters in video header for auto-detection
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        try:
            metrics = calculate_video_metrics(carrier_path, output_path, max_frames=50)
        except Exception as me:
            print(f"Warning: Video metrics calculation failed: {me}")
            metrics = {"psnr": 0, "quality": "Unknown", "description": "Metrics unavailable"}
        
        return {
            "success": True,
            "file_id": file_id,
            "output_filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "encode_info": encode_result,
            "metrics": metrics
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"Video encoding error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Video encoding failed: {str(e)}")
    finally:
        if carrier_path and os.path.exists(carrier_path):
            try:
                os.remove(carrier_path)
            except:
                pass


@app.post("/api/decode/video")
async def decode_video_endpoint(
    stego_video: UploadFile = File(...),
    decryption_key: Optional[str] = Form(None),
    bits_per_channel: Optional[int] = Form(None),
    frame_skip: Optional[int] = Form(None),
    auto_detect: bool = Form(True)
):
    """
    Decode video with auto-detection of encoding parameters.
    
    If auto_detect=True (default), the decoder will attempt to read parameters from the video header.
    If auto_detect=False or parameters not found, uses provided bits_per_channel and frame_skip.
    """
    stego_path = None
    try:
        # Validate provided parameters if given
        if bits_per_channel is not None and (bits_per_channel < 1 or bits_per_channel > 4):
            raise HTTPException(
                status_code=400,
                detail=f"bits_per_channel must be between 1 and 4, got {bits_per_channel}"
            )
        
        if frame_skip is not None and frame_skip < 1:
            raise HTTPException(status_code=400, detail="frame_skip must be at least 1")
        
        if not stego_video.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(stego_video.filename)[1].lower()
        if file_ext not in ['.mp4', '.avi', '.mov', '.mkv']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported: MP4, AVI, MOV, MKV"
            )
        
        file_id = str(uuid.uuid4())
        stego_path = os.path.join(UPLOAD_DIR, f"{file_id}_stego_{stego_video.filename}")
        
        with open(stego_path, "wb") as buffer:
            shutil.copyfileobj(stego_video.file, buffer)
        
        # Decode with auto-detection enabled by default
        extracted_bytes = decode_video_lsb(stego_path, bits_per_channel, frame_skip, auto_detect)
        
        is_encrypted = False
        metadata_str = extracted_bytes.split(b'|', 3)
        
        if len(metadata_str) >= 4 and metadata_str[0] == b'STEGANO':
            is_encrypted = metadata_str[1] == b'True'
            iv_hex = metadata_str[2].decode('utf-8')
            payload_bytes = metadata_str[3]
            
            if is_encrypted:
                if not decryption_key:
                    raise HTTPException(
                        status_code=400,
                        detail="This message is encrypted. Decryption key is required."
                    )
                
                try:
                    iv = bytes.fromhex(iv_hex)
                    payload_bytes = decrypt_payload(payload_bytes, iv, decryption_key)
                except ValueError as ve:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decryption failed: {str(ve)}"
                    )
        else:
            payload_bytes = extracted_bytes
            is_encrypted = False
        
        try:
            payload_text = payload_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Could not decode payload as text. Wrong parameters or corrupted data."
            )
        
        return {
            "success": True,
            "payload": payload_text,
            "payload_size": len(payload_bytes),
            "was_encrypted": is_encrypted
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video decoding failed: {str(e)}")
    finally:
        if stego_path and os.path.exists(stego_path):
            try:
                os.remove(stego_path)
            except:
                pass


@app.post("/api/encode/dct")
async def encode_dct_endpoint(
    carrier: UploadFile = File(...),
    payload_text: str = Form(...),
    encryption_key: Optional[str] = Form(None),
    strength: float = Form(15.0)
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier image provided")
        
        if not payload_text:
            raise HTTPException(status_code=400, detail="No payload text provided")
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format: {file_ext}. Supported: PNG, JPG, BMP, TIFF"
            )
        
        if strength < 1.0 or strength > 100.0:
            raise HTTPException(
                status_code=400,
                detail=f"strength must be between 1.0 and 100.0, got {strength}"
            )
        
        file_id = str(uuid.uuid4())
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            buffer.write(content)
        
        payload_bytes = payload_text.encode('utf-8')
        
        metadata = {}
        if encryption_key:
            try:
                encrypted = encrypt_payload(payload_bytes, encryption_key)
                payload_bytes = encrypted['encrypted_data']
                metadata['iv'] = encrypted['iv'].hex()
                metadata['encrypted'] = True
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Encryption failed: {str(ve)}")
        else:
            metadata['encrypted'] = False
        
        metadata_str = f"STEGANO|{metadata['encrypted']}|{metadata.get('iv', '')}|"
        full_payload = metadata_str.encode('utf-8') + payload_bytes
        
        output_filename = f"{file_id}_stego.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            encode_result = encode_dct(carrier_path, full_payload, output_path, strength)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        try:
            metrics = calculate_metrics(carrier_path, output_path)
        except Exception as me:
            print(f"Warning: Metrics calculation failed: {me}")
            metrics = {"psnr": 0, "ssim": 0, "mse": 0}
        
        return {
            "success": True,
            "file_id": file_id,
            "output_filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "encode_info": encode_result,
            "metrics": metrics
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"DCT encoding error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"DCT encoding failed: {str(e)}")
    finally:
        if carrier_path and os.path.exists(carrier_path):
            try:
                os.remove(carrier_path)
            except:
                pass


@app.post("/api/decode/dct")
async def decode_dct_endpoint(
    stego_image: UploadFile = File(...),
    decryption_key: Optional[str] = Form(None),
    strength: float = Form(15.0)
):
    stego_path = None
    try:
        if strength < 1.0 or strength > 100.0:
            raise HTTPException(
                status_code=400,
                detail=f"strength must be between 1.0 and 100.0, got {strength}"
            )
        
        if not stego_image.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(stego_image.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Use PNG for best results."
            )
        
        file_id = str(uuid.uuid4())
        stego_path = os.path.join(UPLOAD_DIR, f"{file_id}_stego_{stego_image.filename}")
        
        with open(stego_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        
        extracted_bytes = decode_dct(stego_path, strength)
        
        is_encrypted = False
        metadata_str = extracted_bytes.split(b'|', 3)
        
        if len(metadata_str) >= 4 and metadata_str[0] == b'STEGANO':
            is_encrypted = metadata_str[1] == b'True'
            iv_hex = metadata_str[2].decode('utf-8')
            payload_bytes = metadata_str[3]
            
            if is_encrypted:
                if not decryption_key:
                    raise HTTPException(
                        status_code=400,
                        detail="This message is encrypted. Decryption key is required."
                    )
                
                try:
                    iv = bytes.fromhex(iv_hex)
                    payload_bytes = decrypt_payload(payload_bytes, iv, decryption_key)
                except ValueError as ve:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decryption failed: {str(ve)}"
                    )
        else:
            payload_bytes = extracted_bytes
            is_encrypted = False
        
        try:
            payload_text = payload_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Could not decode payload as text. Wrong parameters or corrupted data."
            )
        
        return {
            "success": True,
            "payload": payload_text,
            "payload_size": len(payload_bytes),
            "was_encrypted": is_encrypted
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DCT decoding failed: {str(e)}")
    finally:
        if stego_path and os.path.exists(stego_path):
            try:
                os.remove(stego_path)
            except:
                pass


@app.post("/api/encode/dwt")
async def encode_dwt_endpoint(
    carrier: UploadFile = File(...),
    payload_text: str = Form(...),
    encryption_key: Optional[str] = Form(None),
    wavelet: str = Form("haar"),
    strength: float = Form(0.1)
):
    carrier_path = None
    try:
        if not carrier.filename:
            raise HTTPException(status_code=400, detail="No carrier image provided")
        
        if not payload_text:
            raise HTTPException(status_code=400, detail="No payload text provided")
        
        file_ext = os.path.splitext(carrier.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format: {file_ext}. Supported: PNG, JPG, BMP, TIFF"
            )
        
        if wavelet not in ['haar', 'db1', 'db2', 'db4', 'sym2', 'sym4', 'coif1']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported wavelet: {wavelet}. Supported: haar, db1, db2, db4, sym2, sym4, coif1"
            )
        
        if strength < 0.01 or strength > 10.0:
            raise HTTPException(
                status_code=400,
                detail=f"strength must be between 0.01 and 10.0, got {strength}"
            )
        
        file_id = str(uuid.uuid4())
        carrier_path = os.path.join(UPLOAD_DIR, f"{file_id}_carrier_{carrier.filename}")
        
        with open(carrier_path, "wb") as buffer:
            content = await carrier.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            buffer.write(content)
        
        payload_bytes = payload_text.encode('utf-8')
        
        metadata = {}
        if encryption_key:
            try:
                encrypted = encrypt_payload(payload_bytes, encryption_key)
                payload_bytes = encrypted['encrypted_data']
                metadata['iv'] = encrypted['iv'].hex()
                metadata['encrypted'] = True
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Encryption failed: {str(ve)}")
        else:
            metadata['encrypted'] = False
        
        metadata_str = f"STEGANO|{metadata['encrypted']}|{metadata.get('iv', '')}|"
        full_payload = metadata_str.encode('utf-8') + payload_bytes
        
        output_filename = f"{file_id}_stego.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            encode_result = encode_dwt(carrier_path, full_payload, output_path, wavelet, strength)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        
        try:
            metrics = calculate_metrics(carrier_path, output_path)
        except Exception as me:
            print(f"Warning: Metrics calculation failed: {me}")
            metrics = {"psnr": 0, "ssim": 0, "mse": 0}
        
        return {
            "success": True,
            "file_id": file_id,
            "output_filename": output_filename,
            "download_url": f"/api/download/{output_filename}",
            "encode_info": encode_result,
            "metrics": metrics
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        print(f"DWT encoding error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"DWT encoding failed: {str(e)}")
    finally:
        if carrier_path and os.path.exists(carrier_path):
            try:
                os.remove(carrier_path)
            except:
                pass


@app.post("/api/decode/dwt")
async def decode_dwt_endpoint(
    stego_image: UploadFile = File(...),
    decryption_key: Optional[str] = Form(None),
    wavelet: str = Form("haar"),
    strength: float = Form(0.1)
):
    stego_path = None
    try:
        if wavelet not in ['haar', 'db1', 'db2', 'db4', 'sym2', 'sym4', 'coif1']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported wavelet: {wavelet}. Supported: haar, db1, db2, db4, sym2, sym4, coif1"
            )
        
        if strength < 0.01 or strength > 10.0:
            raise HTTPException(
                status_code=400,
                detail=f"strength must be between 0.01 and 10.0, got {strength}"
            )
        
        if not stego_image.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(stego_image.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Use PNG for best results."
            )
        
        file_id = str(uuid.uuid4())
        stego_path = os.path.join(UPLOAD_DIR, f"{file_id}_stego_{stego_image.filename}")
        
        with open(stego_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        
        extracted_bytes = decode_dwt(stego_path, wavelet, strength)
        
        is_encrypted = False
        metadata_str = extracted_bytes.split(b'|', 3)
        
        if len(metadata_str) >= 4 and metadata_str[0] == b'STEGANO':
            is_encrypted = metadata_str[1] == b'True'
            iv_hex = metadata_str[2].decode('utf-8')
            payload_bytes = metadata_str[3]
            
            if is_encrypted:
                if not decryption_key:
                    raise HTTPException(
                        status_code=400,
                        detail="This message is encrypted. Decryption key is required."
                    )
                
                try:
                    iv = bytes.fromhex(iv_hex)
                    payload_bytes = decrypt_payload(payload_bytes, iv, decryption_key)
                except ValueError as ve:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Decryption failed: {str(ve)}"
                    )
        else:
            payload_bytes = extracted_bytes
            is_encrypted = False
        
        try:
            payload_text = payload_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Could not decode payload as text. Wrong parameters or corrupted data."
            )
        
        return {
            "success": True,
            "payload": payload_text,
            "payload_size": len(payload_bytes),
            "was_encrypted": is_encrypted
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DWT decoding failed: {str(e)}")
    finally:
        if stego_path and os.path.exists(stego_path):
            try:
                os.remove(stego_path)
            except:
                pass


# ===== NEW AI-POWERED ENDPOINTS =====

@app.post("/api/ai/chat")
async def ai_chat(
    question: str = Form(...),
    context: Optional[str] = Form(None)
):
    """
    AI Chat Assistant - Answer questions about steganography
    """
    try:
        explainer = get_explainer()
        
        # Parse context if provided
        context_dict = None
        if context:
            try:
                import json
                context_dict = json.loads(context)
            except:
                pass
        
        response = explainer.chat_response(question, context_dict)
        
        return {
            "success": True,
            "question": question,
            "response": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")


@app.post("/api/ai/explain-algorithm")
async def explain_algorithm(
    algorithm: str = Form(...),
    image_stats: str = Form(...),
    recommendation: str = Form(...)
):
    """
    Get AI explanation for why an algorithm was recommended
    """
    try:
        import json
        explainer = get_explainer()
        
        stats = json.loads(image_stats)
        rec = json.loads(recommendation)
        
        explanation = explainer.explain_algorithm_choice(algorithm, stats, rec)
        
        return {
            "success": True,
            "algorithm": algorithm,
            "explanation": explanation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI explanation failed: {str(e)}")


@app.post("/api/ai/security-analysis")
async def security_analysis(
    metrics: str = Form(...),
    algorithm: str = Form(...),
    settings: str = Form(...)
):
    """
    Get detailed security risk analysis
    """
    try:
        import json
        explainer = get_explainer()
        
        metrics_dict = json.loads(metrics)
        settings_dict = json.loads(settings)
        
        analysis = explainer.explain_security_risk(metrics_dict, algorithm, settings_dict)
        
        return {
            "success": True,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security analysis failed: {str(e)}")


@app.post("/api/ai/compare-algorithms")
async def compare_algorithms(
    algorithm1: str = Form(...),
    algorithm2: str = Form(...)
):
    """
    Compare two steganography algorithms
    """
    try:
        explainer = get_explainer()
        
        comparison = explainer.generate_comparison(algorithm1, algorithm2)
        
        return {
            "success": True,
            "algorithm1": algorithm1,
            "algorithm2": algorithm2,
            "comparison": comparison
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm comparison failed: {str(e)}")


@app.post("/api/ai/steganalysis")
async def steganalysis(
    image: UploadFile = File(...)
):
    """
    Analyze image for potential steganography (Detection)
    """
    image_path = None
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image provided")
        
        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {file_ext}. Use PNG, JPG, BMP, or TIFF."
            )
        
        # Save temporary file
        file_id = str(uuid.uuid4())
        image_path = os.path.join(UPLOAD_DIR, f"{file_id}_analysis_{image.filename}")
        
        with open(image_path, "wb") as buffer:
            content = await image.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file")
            if len(content) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image too large. Max: 50MB")
            buffer.write(content)
        
        # Run steganalysis
        detector = get_detector()
        results = detector.analyze_for_steganography(image_path)
        
        return {
            "success": True,
            "filename": image.filename,
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Steganalysis error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Steganalysis failed: {str(e)}")
    finally:
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass


@app.post("/api/ai/generate-report")
async def generate_report(
    operation_data: str = Form(...)
):
    """
    Generate comprehensive PDF report for steganography operation
    """
    try:
        import json
        
        # Parse operation data
        data = json.loads(operation_data)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        report_filename = f"{file_id}_report.pdf"
        report_path = os.path.join(OUTPUT_DIR, report_filename)
        
        # Generate report
        generator = get_report_generator()
        generator.generate_encode_report(data, report_path, include_images=False)
        
        return {
            "success": True,
            "report_filename": report_filename,
            "download_url": f"/api/download/{report_filename}"
        }
    
    except Exception as e:
        import traceback
        print(f"Report generation error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/api/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
