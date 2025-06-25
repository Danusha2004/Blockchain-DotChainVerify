from blake3 import blake3
import qrcode

# 🔒 1️⃣ Generate Blake3 Hash
def generate_blake3_hash(passport_number):
    """Generate Blake3 hash of the passport number."""
    hash_value = blake3(passport_number.encode()).hexdigest()
    print(f"[✔️] Blake3 Hash: {hash_value}")
    return hash_value

# 🔗 2️⃣ Generate QR Code
def generate_qr_code(data, output_file="passport_qr.png"):
    """Generate a QR code from the hash."""
    qr = qrcode.make(data)
    qr.save(output_file)
    print(f"[✔️] QR Code saved at: {output_file}")
    return output_file

# 🚀 Main Execution
def main():
    # Replace with your actual passport number or take input
    passport_number = input("Enter passport number: ").strip().upper()

    # Step 1: Hash the passport number
    blake3_hash = generate_blake3_hash(passport_number)

    # Step 2: Generate QR code from the hash
    qr_file = generate_qr_code(blake3_hash)

    print("\n✅ FINAL OUTPUT")
    print(f"📄 Passport Number: {passport_number}")
    print(f"🔒 Blake3 Hash: {blake3_hash}")
    print(f"🔗 QR Code File: {qr_file}")

if __name__ == "__main__":
    main()
