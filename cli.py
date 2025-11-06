import argparse
from core.steganography import embed_file_into_image, extract_file_from_image, capacity_bytes_from_image
from io_utils.file_handler import normalize_path
import os
import sys
from PIL import Image

def cmd_embed(args):
    cover = normalize_path(args.cover)
    secret = normalize_path(args.secret)
    out = normalize_path(args.out) if args.out else 'stego_output.png'

    print("\nChoose bit position to modify:")
    print("1 → Least significant bits (LSB, least visible)")
    print("2 → Middle bits")
    print("3 → Most significant bits (MSB, most visible)")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        bit_position = "lsb"
    elif choice == "2":
        bit_position = "mid"
    elif choice == "3":
        bit_position = "msb"
    else:
        print("Invalid choice! Defaulting to LSB.")
        bit_position = "lsb"

    try:
        embed_file_into_image(cover, secret, out, bits_per_channel=2, verbose=True, bit_position=bit_position)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def cmd_extract(args):
    stego = normalize_path(args.stego)
    outdir = normalize_path(args.out) if args.out else '.'

    print("\nEnter the same bit position used during embedding:")
    print("1 → LSB")
    print("2 → Middle bits")
    print("3 → MSB")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        bit_position = "lsb"
    elif choice == "2":
        bit_position = "mid"
    elif choice == "3":
        bit_position = "msb"
    else:
        print("Invalid choice! Defaulting to LSB.")
        bit_position = "lsb"

    try:
        extract_file_from_image(stego, output_folder=outdir, bits_per_channel=2, verbose=True, bit_position=bit_position)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def cmd_info(args):
    cover = normalize_path(args.cover)
    if not os.path.exists(cover):
        print("Cover image not found.")
        return
    with Image.open(cover) as img:
        img = img.convert('RGB')
        cap = capacity_bytes_from_image(img, bits_per_channel=2)
        print(f"Cover image: {cover}")
        print(f"Dimensions: {img.size[0]} x {img.size[1]}")
        print(f"Approx capacity: {cap} bytes")


def build_parser():
    p = argparse.ArgumentParser(description="Image Steganography — embed/extract files in PNG images (2-bit flexible)")
    sub = p.add_subparsers(dest='cmd')

    pe = sub.add_parser('embed', help='Embed a secret file into a cover image')
    pe.add_argument('--cover', required=True, help='Path to cover image (PNG/JPG recommended)')
    pe.add_argument('--secret', required=True, help='Path to secret file to hide (any type)')
    pe.add_argument('--out', required=False, help='Path for output stego PNG (default: stego_output.png)')

    px = sub.add_parser('extract', help='Extract secret file from a stego image')
    px.add_argument('--stego', required=True, help='Path to stego image (PNG)')
    px.add_argument('--out', required=False, help='Output folder for extracted file (default: current dir)')

    pi = sub.add_parser('info', help='Show cover image capacity info')
    pi.add_argument('--cover', required=True, help='Path to cover image')

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.cmd == 'embed':
        cmd_embed(args)
    elif args.cmd == 'extract':
        cmd_extract(args)
    elif args.cmd == 'info':
        cmd_info(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
