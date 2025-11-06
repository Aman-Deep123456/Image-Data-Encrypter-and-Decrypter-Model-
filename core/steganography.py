from PIL import Image
import numpy as np
import os

MAGIC = b'STEG'

def _human_readable(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TB"

def capacity_bytes_from_image(img: Image.Image, bits_per_channel: int = 2) -> int:
    w, h = img.size
    total_bits = w * h * 3 * bits_per_channel
    return total_bits // 8

def _payload_build(secret_bytes: bytes, original_name: str) -> bytes:
    name_bytes = original_name.encode('utf-8')
    header = MAGIC
    header += len(secret_bytes).to_bytes(8, 'big')
    header += len(name_bytes).to_bytes(2, 'big')
    header += name_bytes
    return header + secret_bytes

def _payload_parse(payload_bytes: bytes):
    if payload_bytes[:4] != MAGIC:
        raise ValueError("Invalid or missing header.")
    offset = 4
    payload_len = int.from_bytes(payload_bytes[offset:offset+8], 'big'); offset += 8
    name_len = int.from_bytes(payload_bytes[offset:offset+2], 'big'); offset += 2
    name = payload_bytes[offset:offset+name_len].decode('utf-8'); offset += name_len
    secret = payload_bytes[offset:offset+payload_len]
    return name, secret


def embed_file_into_image(cover_image_path, secret_file_path, output_image_path, bits_per_channel=2, verbose=True, bit_position="lsb"):
    with Image.open(cover_image_path) as img:
        img = img.convert('RGB')
        w, h = img.size
        cap_bytes = capacity_bytes_from_image(img, bits_per_channel)
        if verbose:
            print(f"Cover image size: {w}x{h} — capacity ≈ {_human_readable(cap_bytes)}")

        with open(secret_file_path, 'rb') as f:
            secret_bytes = f.read()
        payload = _payload_build(secret_bytes, os.path.basename(secret_file_path))
        payload_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
        needed_bits = len(payload_bits)
        capacity_bits = w * h * 3 * bits_per_channel
        if needed_bits > capacity_bits:
            raise ValueError("Secret too large for cover image capacity.")

        arr = np.array(img, dtype=np.uint8)
        flat = arr.reshape(-1, 3).flatten().astype(np.uint16)

        # Determine bit position mask and shift
        if bit_position == "lsb":
            mask = 0b11111100
            shift = 0
        elif bit_position == "mid":
            mask = 0b11110011
            shift = 2
        elif bit_position == "msb":
            mask = 0b00111111
            shift = 6
        else:
            raise ValueError("Invalid bit position option. Choose from 'lsb', 'mid', or 'msb'.")

        # Two-bit encoding
        if len(payload_bits) % 2 != 0:
            payload_bits = np.append(payload_bits, 0)
        two_bit_vals = (payload_bits[::2] << 1) | payload_bits[1::2]
        slots = len(two_bit_vals)

        flat[:slots] = ((flat[:slots] & mask) | (two_bit_vals << shift)).astype(np.uint8)

        new_arr = flat.reshape(arr.shape)
        Image.fromarray(new_arr.astype(np.uint8), 'RGB').save(output_image_path, 'PNG')
        if verbose:
            print(f"✅ Success — stego image written: {output_image_path}")


def extract_file_from_image(stego_image_path, output_folder='.', bits_per_channel=2, verbose=True, bit_position="lsb"):
    with Image.open(stego_image_path) as img:
        img = img.convert('RGB')
        w, h = img.size
        if verbose:
            print(f"Reading stego image: {w}x{h}")

        arr = np.array(img, dtype=np.uint8)
        flat = arr.reshape(-1, 3).flatten()

        # Determine bit position mask and shift
        if bit_position == "lsb":
            shift = 0
        elif bit_position == "mid":
            shift = 2
        elif bit_position == "msb":
            shift = 6
        else:
            raise ValueError("Invalid bit position option. Choose from 'lsb', 'mid', or 'msb'.")

        vals = ((flat >> shift) & 0b11).astype(np.uint8)
        bits = np.empty(len(vals) * 2, dtype=np.uint8)
        bits[::2] = (vals >> 1) & 1
        bits[1::2] = vals & 1

        header_bytes = np.packbits(bits[:14*8])
        if bytes(header_bytes[:4]) != MAGIC:
            raise ValueError("No hidden data found in image.")
        payload_len = int.from_bytes(bytes(header_bytes[4:12]), 'big')
        name_len = int.from_bytes(bytes(header_bytes[12:14]), 'big')
        total_len = 14 + name_len + payload_len
        total_bits = total_len * 8
        payload = np.packbits(bits[:total_bits])
        name, secret = _payload_parse(payload.tobytes())
        os.makedirs(output_folder, exist_ok=True)
        out_path = os.path.join(output_folder, name)
        with open(out_path, 'wb') as f:
            f.write(secret)
        if verbose:
            print(f"✅ Extracted file saved to: {out_path}")
        return out_path
 