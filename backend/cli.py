#!/usr/bin/env python3
import click
import os
import sys
from colorama import Fore, Style, init

init(autoreset=True)

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
from stego.analyzer import analyze_image


@click.group()
@click.version_option(version='1.0.0')
def cli():
    pass


@cli.command()
@click.option('--carrier', '-c', required=True, type=click.Path(exists=True), help='Carrier file (image/audio/video)')
@click.option('--payload', '-p', required=True, help='Text payload or path to file (prefix with file:)')
@click.option('--output', '-o', required=True, type=click.Path(), help='Output stego file path')
@click.option('--algorithm', '-a', type=click.Choice(['lsb', 'dct', 'dwt', 'audio', 'video']), default='lsb', help='Steganography algorithm')
@click.option('--bits', '-b', type=int, default=1, help='Bits per channel/sample (1-4)')
@click.option('--key', '-k', default=None, help='Encryption key (optional)')
@click.option('--strength', '-s', type=float, default=10.0, help='Embedding strength for DCT/DWT')
@click.option('--wavelet', '-w', default='haar', help='Wavelet for DWT (haar, db1, sym2, etc.)')
@click.option('--frame-skip', type=int, default=1, help='Frame skip for video (1=every frame)')
def encode(carrier, payload, output, algorithm, bits, key, strength, wavelet, frame_skip):
    try:
        click.echo(f"{Fore.CYAN}SteganoGen - Encoding{Style.RESET_ALL}")
        click.echo(f"Carrier: {carrier}")
        click.echo(f"Algorithm: {algorithm.upper()}")
        
        if payload.startswith('file:'):
            payload_path = payload[5:]
            if not os.path.exists(payload_path):
                click.echo(f"{Fore.RED}Error: Payload file not found: {payload_path}{Style.RESET_ALL}")
                sys.exit(1)
            with open(payload_path, 'rb') as f:
                payload_bytes = f.read()
            click.echo(f"Payload: File ({len(payload_bytes)} bytes)")
        else:
            payload_bytes = payload.encode('utf-8')
            click.echo(f"Payload: Text ({len(payload_bytes)} bytes)")
        
        if key:
            encrypted = encrypt_payload(payload_bytes, key)
            payload_bytes = encrypted['encrypted_data']
            metadata = f"STEGANO|True|{encrypted['iv'].hex()}|".encode('utf-8')
            payload_bytes = metadata + payload_bytes
            click.echo(f"{Fore.GREEN}Encryption: Enabled{Style.RESET_ALL}")
        else:
            metadata = b"STEGANO|False||"
            payload_bytes = metadata + payload_bytes
        
        if algorithm == 'lsb':
            result = encode_lsb(carrier, payload_bytes, output, bits)
        elif algorithm == 'dct':
            result = encode_dct(carrier, payload_bytes, output, strength)
        elif algorithm == 'dwt':
            result = encode_dwt(carrier, payload_bytes, output, wavelet, strength)
        elif algorithm == 'audio':
            result = encode_audio_lsb(carrier, payload_bytes, output, bits)
        elif algorithm == 'video':
            result = encode_video_lsb(
                carrier, 
                payload_bytes, 
                output, 
                bits, 
                frame_skip,
                use_uncompressed=True,  # Use lossless codec
                store_params=True       # Store parameters for auto-detection
            )
        
        click.echo(f"{Fore.GREEN}✓ Encoding successful!{Style.RESET_ALL}")
        click.echo(f"Output: {output}")
        click.echo(f"Capacity used: {result['capacity_used']:.2f}%")
        click.echo(f"Payload size: {result['payload_size']} bytes")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.option('--stego', '-s', required=True, type=click.Path(exists=True), help='Stego file (image/audio/video)')
@click.option('--output', '-o', type=click.Path(), help='Output file for extracted payload (optional)')
@click.option('--algorithm', '-a', type=click.Choice(['lsb', 'dct', 'dwt', 'audio', 'video']), default='lsb', help='Steganography algorithm')
@click.option('--bits', '-b', type=int, default=None, help='Bits per channel/sample (1-4). For video: auto-detected if not provided')
@click.option('--key', '-k', default=None, help='Decryption key (if encrypted)')
@click.option('--strength', type=float, default=10.0, help='Embedding strength for DCT/DWT')
@click.option('--wavelet', '-w', default='haar', help='Wavelet for DWT')
@click.option('--frame-skip', type=int, default=None, help='Frame skip for video. Auto-detected if not provided')
@click.option('--no-auto-detect', is_flag=True, help='Disable auto-detection for video (use provided parameters)')
def decode(stego, output, algorithm, bits, key, strength, wavelet, frame_skip, no_auto_detect):
    try:
        click.echo(f"{Fore.CYAN}SteganoGen - Decoding{Style.RESET_ALL}")
        click.echo(f"Stego file: {stego}")
        click.echo(f"Algorithm: {algorithm.upper()}")
        
        if algorithm == 'lsb':
            if bits is None:
                bits = 1
            extracted_bytes = decode_lsb(stego, bits)
        elif algorithm == 'dct':
            extracted_bytes = decode_dct(stego, strength)
        elif algorithm == 'dwt':
            extracted_bytes = decode_dwt(stego, wavelet, strength)
        elif algorithm == 'audio':
            if bits is None:
                bits = 2
            extracted_bytes = decode_audio_lsb(stego, bits)
        elif algorithm == 'video':
            auto_detect = not no_auto_detect
            if auto_detect:
                click.echo(f"{Fore.CYAN}Auto-detecting parameters from video...{Style.RESET_ALL}")
            extracted_bytes = decode_video_lsb(stego, bits, frame_skip, auto_detect)
        
        is_encrypted = False
        metadata_parts = extracted_bytes.split(b'|', 3)
        
        if len(metadata_parts) >= 4 and metadata_parts[0] == b'STEGANO':
            is_encrypted = metadata_parts[1] == b'True'
            iv_hex = metadata_parts[2].decode('utf-8')
            payload_bytes = metadata_parts[3]
            
            if is_encrypted:
                if not key:
                    click.echo(f"{Fore.RED}Error: Payload is encrypted. Provide decryption key with --key{Style.RESET_ALL}")
                    sys.exit(1)
                
                iv = bytes.fromhex(iv_hex)
                payload_bytes = decrypt_payload(payload_bytes, iv, key)
                click.echo(f"{Fore.GREEN}Decryption: Successful{Style.RESET_ALL}")
        else:
            payload_bytes = extracted_bytes
        
        if output:
            with open(output, 'wb') as f:
                f.write(payload_bytes)
            click.echo(f"{Fore.GREEN}✓ Decoding successful!{Style.RESET_ALL}")
            click.echo(f"Output saved to: {output}")
            click.echo(f"Size: {len(payload_bytes)} bytes")
        else:
            try:
                payload_text = payload_bytes.decode('utf-8')
                click.echo(f"{Fore.GREEN}✓ Decoding successful!{Style.RESET_ALL}")
                click.echo(f"Extracted payload (text):")
                click.echo(f"{Fore.YELLOW}{payload_text}{Style.RESET_ALL}")
            except UnicodeDecodeError:
                click.echo(f"{Fore.GREEN}✓ Decoding successful!{Style.RESET_ALL}")
                click.echo(f"Extracted payload (binary, {len(payload_bytes)} bytes)")
                click.echo(f"Use --output to save binary data to file")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


@cli.command()
@click.argument('image', type=click.Path(exists=True))
def analyze(image):
    try:
        click.echo(f"{Fore.CYAN}SteganoGen - Image Analysis{Style.RESET_ALL}")
        click.echo(f"Analyzing: {image}")
        
        stats = analyze_image(image)
        
        click.echo(f"\n{Fore.YELLOW}Image Properties:{Style.RESET_ALL}")
        click.echo(f"  Dimensions: {stats['width']}x{stats['height']}")
        click.echo(f"  Format: {stats['format']}")
        click.echo(f"  Total Pixels: {stats['total_pixels']:,}")
        
        click.echo(f"\n{Fore.YELLOW}Quality Metrics:{Style.RESET_ALL}")
        click.echo(f"  Entropy: {stats['entropy']} bits")
        click.echo(f"  Variance: {stats['variance']}")
        click.echo(f"  Edge Density: {stats['edge_density']}")
        click.echo(f"  Texture Score: {stats['texture_score']}")
        click.echo(f"  Noise Level: {stats['noise_level']}")
        click.echo(f"  Uniformity: {stats['uniformity']}")
        click.echo(f"  Smoothness: {stats['smoothness']}")
        
        click.echo(f"\n{Fore.YELLOW}Capacity Analysis:{Style.RESET_ALL}")
        click.echo(f"  1 bit/channel: {stats['capacity_at_1bit']:,} bytes ({stats['capacity_at_1bit'] / 1024:.2f} KB)")
        click.echo(f"  2 bits/channel: {stats['capacity_at_2bit']:,} bytes ({stats['capacity_at_2bit'] / 1024:.2f} KB)")
        click.echo(f"  4 bits/channel: {stats['capacity_at_4bit']:,} bytes ({stats['capacity_at_4bit'] / 1024:.2f} KB)")
        
        click.echo(f"\n{Fore.YELLOW}Suitability:{Style.RESET_ALL}")
        click.echo(f"  {stats['suitability']}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
