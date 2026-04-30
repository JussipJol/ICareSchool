import qrcode
import os
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_school_qr(school_slug: str, base_url: str):
    url = f"{base_url}/app/index.html?school={school_slug}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#003366", back_color="white").convert('RGB')
    
    os.makedirs("../qrcodes", exist_ok=True)
    filename = f"../qrcodes/{school_slug}.png"
    img.save(filename)
    return filename

if __name__ == "__main__":
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:8000"
    print(f"Generating test QR codes for IP: {local_ip}...")
    generate_school_qr("school-lyceum-1", base_url)
    generate_school_qr("school-gymnasium-3", base_url)
    print("Done! Check the 'qrcodes' folder.")
