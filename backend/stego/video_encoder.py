import numpy as np
import cv2
import struct
import os
import tempfile


def encode_video_lsb(video_path: str, payload: bytes, output_path: str, bits_per_channel: int = 1, frame_skip: int = 1, use_uncompressed: bool = True, store_params: bool = True) -> dict:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if bits_per_channel < 1 or bits_per_channel > 4:
        raise ValueError(f"bits_per_channel must be between 1 and 4, got {bits_per_channel}")
    
    if frame_skip < 1:
        raise ValueError(f"frame_skip must be at least 1, got {frame_skip}")
    
    if not payload:
        raise ValueError("Payload cannot be empty")
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Use FFV1 codec for truly lossless video, fallback to uncompressed
        # FFV1 is lossless and provides better file sizes than raw
        if use_uncompressed:
            try:
                # Try FFV1 lossless codec first (best option)
                fourcc = cv2.VideoWriter_fourcc(*'FFV1')
            except:
                try:
                    # Fallback to MJPEG at 100% quality (lossy but commonly supported)
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                except:
                    # Last resort: uncompressed
                    fourcc = 0
        else:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        
        if fps <= 0 or width <= 0 or height <= 0 or total_frames <= 0:
            raise ValueError("Invalid video properties")
        
    except Exception as e:
        raise ValueError(f"Failed to read video properties: {str(e)}")
    
    usable_frames = total_frames // frame_skip
    max_bytes_per_frame = (width * height * 3 * bits_per_channel) // 8
    max_bytes = max_bytes_per_frame * usable_frames
    
    payload_length = len(payload)
    header_size = 4
    required_bytes = payload_length + header_size
    
    if required_bytes > max_bytes:
        cap.release()
        raise ValueError(
            f"Payload too large for video file.\n"
            f"Required: {required_bytes} bytes (payload: {payload_length} + header: {header_size})\n"
            f"Available: {max_bytes} bytes across {usable_frames} frames\n"
            f"Try using a longer video, reducing frame_skip (current: {frame_skip}), or increasing bits_per_channel (current: {bits_per_channel})"
        )
    
    if payload_length > 2**32 - 1:
        cap.release()
        raise ValueError(f"Payload too large: {payload_length} bytes (max: {2**32 - 1})")
    
    # Add parameter header: magic bytes (4), bits_per_channel (1), frame_skip (1), payload_length (4)
    # Magic: "VSTG" = Video STeGanography
    if store_params:
        header = b'VSTG' + struct.pack('BB', bits_per_channel, frame_skip) + struct.pack('>I', payload_length)
        full_payload = header + payload
        header_info = f"with parameter header (10 bytes)"
    else:
        # Legacy format without parameter storage
        length_bytes = struct.pack('>I', payload_length)
        full_payload = length_bytes + payload
        header_info = f"legacy format (4 bytes header)"
    
    payload_bits = []
    for byte in full_payload:
        for i in range(8):
            payload_bits.append((byte >> (7 - i)) & 1)
    
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            raise IOError("Failed to create output video writer")
        
        frame_count = 0
        bit_index = 0
        frames_modified = 0
        
        bit_mask = (1 << bits_per_channel) - 1
        clear_mask = ~bit_mask & 0xFF
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0 and bit_index < len(payload_bits):
                flat_frame = frame.flatten()
                
                for i in range(len(flat_frame)):
                    if bit_index >= len(payload_bits):
                        break
                    
                    bits_to_embed = 0
                    for j in range(bits_per_channel):
                        if bit_index < len(payload_bits):
                            bits_to_embed = (bits_to_embed << 1) | payload_bits[bit_index]
                            bit_index += 1
                        else:
                            bits_to_embed = bits_to_embed << 1
                    
                    flat_frame[i] = (flat_frame[i] & clear_mask) | bits_to_embed
                
                frame = flat_frame.reshape(frame.shape)
                frames_modified += 1
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()
        
    except Exception as e:
        cap.release()
        if 'out' in locals():
            out.release()
        raise IOError(f"Failed to encode video: {str(e)}")
    
    duration = total_frames / fps
    
    return {
        'success': True,
        'payload_size': payload_length,
        'capacity_used': (required_bytes / max_bytes) * 100,
        'bits_per_channel': bits_per_channel,
        'frame_skip': frame_skip,
        'total_frames': total_frames,
        'frames_modified': frames_modified,
        'dimensions': f"{width}x{height}",
        'fps': round(fps, 2),
        'duration': round(duration, 2),
        'max_capacity_bytes': max_bytes,
        'parameters_stored': store_params,
        'header_format': header_info if store_params else 'legacy'
    }
