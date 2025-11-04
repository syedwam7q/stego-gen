import numpy as np
import cv2
import struct
import os


def decode_video_lsb(video_path: str, bits_per_channel: int = None, frame_skip: int = None, auto_detect: bool = True) -> bytes:
    """
    Decode hidden data from video using LSB steganography.
    
    Args:
        video_path: Path to stego video file
        bits_per_channel: Bits per channel (1-4). If None and auto_detect=True, will be read from header.
        frame_skip: Frame skip value. If None and auto_detect=True, will be read from header.
        auto_detect: If True, attempts to read parameters from video header (new format).
                    If False or header not found, uses provided parameters (legacy format).
    
    Returns:
        Extracted payload bytes
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Validation will be done after determining actual parameters
    provided_bits = bits_per_channel
    provided_skip = frame_skip
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video file")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if width <= 0 or height <= 0 or total_frames <= 0:
            raise ValueError("Invalid video properties")
        
    except Exception as e:
        raise ValueError(f"Failed to read video properties: {str(e)}")
    
    # First, try to detect parameters from header if auto_detect is enabled
    detected_params = False
    using_legacy = False
    
    if auto_detect:
        # Try multiple parameter combinations to detect the header
        # The header is encoded with the same bits_per_channel as the payload
        # So we need to try different values to find the right one
        
        test_combinations = [
            (1, 1), (2, 1), (3, 1), (4, 1),  # Common: 1-4 bits, frame_skip=1
            (1, 2), (2, 2),                   # Less common
        ]
        
        for temp_bits, temp_skip in test_combinations:
            try:
                # Reset to beginning for each attempt
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                temp_mask = (1 << temp_bits) - 1
                
                # Extract first 80 bits (10 bytes) to check for magic header
                header_bits = []
                frame_count = 0
                
                while len(header_bits) < 80:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % temp_skip == 0:
                        flat_frame = frame.flatten()
                        for pixel_value in flat_frame:
                            if len(header_bits) >= 80:
                                break
                            bits = pixel_value & temp_mask
                            for i in range(temp_bits - 1, -1, -1):
                                header_bits.append((bits >> i) & 1)
                    frame_count += 1
                
                # Convert bits to bytes
                header_bytes = []
                for i in range(0, min(80, len(header_bits)), 8):
                    if i + 8 <= len(header_bits):
                        byte = 0
                        for j in range(8):
                            byte = (byte << 1) | header_bits[i + j]
                        header_bytes.append(byte)
                
                header_bytes = bytes(header_bytes[:10])
                
                # Check for magic header "VSTG"
                if header_bytes[:4] == b'VSTG':
                    bits_per_channel = header_bytes[4]
                    frame_skip = header_bytes[5]
                    
                    # Validate that detected parameters make sense
                    if 1 <= bits_per_channel <= 4 and 1 <= frame_skip <= 255:
                        detected_params = True
                        print(f"[Video Decoder] ✓ Auto-detected parameters: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}")
                        break
                    
            except Exception as e:
                continue
        
        if not detected_params:
            print(f"[Video Decoder] Auto-detection failed - no valid header found")
            using_legacy = True
        
        # Reset video capture to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        using_legacy = True
    
    # If auto-detection was disabled, still try to detect if new format exists
    # This allows explicit parameters to work with both new and legacy formats
    if not auto_detect and not detected_params:
        # Quick check: try to read header with provided parameters
        if provided_bits and provided_skip:
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                temp_mask = (1 << provided_bits) - 1
                
                header_bits = []
                frame_count = 0
                
                while len(header_bits) < 80:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % provided_skip == 0:
                        flat_frame = frame.flatten()
                        for pixel_value in flat_frame:
                            if len(header_bits) >= 80:
                                break
                            bits = pixel_value & temp_mask
                            for i in range(provided_bits - 1, -1, -1):
                                header_bits.append((bits >> i) & 1)
                    frame_count += 1
                
                header_bytes = []
                for i in range(0, min(80, len(header_bits)), 8):
                    if i + 8 <= len(header_bits):
                        byte = 0
                        for j in range(8):
                            byte = (byte << 1) | header_bits[i + j]
                        header_bytes.append(byte)
                
                header_bytes = bytes(header_bytes[:10])
                
                if header_bytes[:4] == b'VSTG':
                    detected_params = True
                    bits_per_channel = header_bytes[4]
                    frame_skip = header_bytes[5]
                    using_legacy = False
                    print(f"[Video Decoder] Detected new format with provided parameters: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}")
                else:
                    using_legacy = True
                    
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            except:
                using_legacy = True
    
    # If using legacy format or auto-detection failed, use provided parameters
    if using_legacy:
        if bits_per_channel is None:
            bits_per_channel = provided_bits if provided_bits else 1
        if frame_skip is None:
            frame_skip = provided_skip if provided_skip else 1
        print(f"[Video Decoder] Using legacy format with parameters: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}")
    
    # Validate parameters
    if bits_per_channel < 1 or bits_per_channel > 4:
        cap.release()
        raise ValueError(f"bits_per_channel must be between 1 and 4, got {bits_per_channel}")
    
    if frame_skip < 1:
        cap.release()
        raise ValueError(f"frame_skip must be at least 1, got {frame_skip}")
    
    usable_frames = total_frames // frame_skip
    max_bytes_per_frame = (width * height * 3 * bits_per_channel) // 8
    max_extractable_bytes = max_bytes_per_frame * usable_frames
    
    # Determine header size based on format
    header_size = 10 if detected_params else 4
    
    if max_extractable_bytes < header_size:
        cap.release()
        raise ValueError(
            f"Video too small to contain hidden data. "
            f"Can extract only {max_extractable_bytes} bytes (need at least {header_size} for header)"
        )
    
    bit_mask = (1 << bits_per_channel) - 1
    
    try:
        extracted_bits = []
        frame_count = 0
        payload_length = None
        
        # Calculate bits needed for header based on format
        if detected_params:
            # New format: 10 bytes header (80 bits)
            header_bits_needed = 80
            length_offset = 48  # After "VSTG" (32 bits) + bits_per_channel (8) + frame_skip (8)
        else:
            # Legacy format: 4 bytes header (32 bits)
            header_bits_needed = 32
            length_offset = 0
        
        total_bits_needed = header_bits_needed
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                flat_frame = frame.flatten()
                
                for pixel_value in flat_frame:
                    if len(extracted_bits) >= total_bits_needed:
                        break
                    
                    bits = pixel_value & bit_mask
                    for i in range(bits_per_channel - 1, -1, -1):
                        extracted_bits.append((bits >> i) & 1)
                        
                        # Check if we've read the header
                        if len(extracted_bits) == header_bits_needed and payload_length is None:
                            # Extract length from the appropriate position
                            length_bits = extracted_bits[length_offset:length_offset + 32]
                            length_bytes = []
                            for j in range(0, 32, 8):
                                byte = 0
                                for k in range(8):
                                    byte = (byte << 1) | length_bits[j + k]
                                length_bytes.append(byte)
                            
                            try:
                                payload_length = struct.unpack('>I', bytes(length_bytes))[0]
                            except struct.error as e:
                                cap.release()
                                raise ValueError(f"Failed to unpack payload length: {str(e)}")
                            
                            # Comprehensive validation of payload length
                            if payload_length == 0:
                                cap.release()
                                raise ValueError(
                                    "Payload length is zero. Video may not contain hidden data.\n"
                                    f"Using: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}"
                                )
                            
                            # Check against maximum extractable capacity
                            max_payload = max_extractable_bytes - header_size
                            if payload_length > max_payload:
                                cap.release()
                                error_msg = (
                                    f"Invalid payload length: {payload_length:,} bytes. "
                                    f"Maximum extractable: {max_payload:,} bytes.\n"
                                    f"Current parameters: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}\n"
                                )
                                if detected_params:
                                    error_msg += "Parameters were auto-detected from video header."
                                else:
                                    error_msg += (
                                        "Using provided/default parameters. This video might:\n"
                                        "  1. Be encoded with different parameters\n"
                                        "  2. Not contain hidden data\n"
                                        "  3. Be corrupted or compressed after encoding\n"
                                        f"Suggested: Try bits_per_channel in [1,2,3,4] and frame_skip in [1,2,5,10]"
                                    )
                                raise ValueError(error_msg)
                            
                            # Sanity check: payload shouldn't be unreasonably large
                            if payload_length > 100 * 1024 * 1024:  # 100 MB
                                cap.release()
                                raise ValueError(
                                    f"Payload length suspiciously large: {payload_length:,} bytes (>100MB). "
                                    f"This likely indicates wrong decoding parameters.\n"
                                    f"Current: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}"
                                )
                            
                            total_bits_needed = header_bits_needed + (payload_length * 8)
                        
                        if len(extracted_bits) >= total_bits_needed:
                            break
                
                if len(extracted_bits) >= total_bits_needed:
                    break
            
            frame_count += 1
        
        cap.release()
        
        if len(extracted_bits) < header_bits_needed:
            raise ValueError(f"Not enough bits to extract header. Need {header_bits_needed}, have {len(extracted_bits)}")
        
        if len(extracted_bits) < total_bits_needed:
            raise ValueError(
                f"Not enough bits in video to extract payload. "
                f"Need {total_bits_needed} bits, have {len(extracted_bits)} bits. "
                f"Using: bits_per_channel={bits_per_channel}, frame_skip={frame_skip}"
            )
        
        # Extract payload bits (skip header)
        payload_start = header_bits_needed
        payload_bits = extracted_bits[payload_start:payload_start + (payload_length * 8)]
        
        payload_bytes = []
        for i in range(0, len(payload_bits), 8):
            if i + 8 <= len(payload_bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | payload_bits[i + j]
                payload_bytes.append(byte)
        
        if len(payload_bytes) != payload_length:
            raise ValueError(
                f"Extracted byte count mismatch. Expected {payload_length}, got {len(payload_bytes)}"
            )
        
        return bytes(payload_bytes)
        
    except Exception as e:
        if cap.isOpened():
            cap.release()
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to decode video: {str(e)}")
