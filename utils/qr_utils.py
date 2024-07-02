# solana-webwallet/utils/qr_utils.py


import re
from io import BytesIO

import qrcode
from aiogram.types import BufferedInputFile
from asgiref.sync import sync_to_async

from applications.wallet.models import Wallet


@sync_to_async
def generate_qr_code(wallet: Wallet, box_size: int = 10, border: int = 4):
    # Объединяем имя кошелька, описание и адрес в одну строку
    data = (f"Wallet name: {wallet.name}\nWallet description: {wallet.description}\n"
            f"Wallet address: {wallet.wallet_address}")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    # Сохраняем изображение QR-кода в bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # # Создаем экземпляр модели QRCode и сохраняем его в базе данных
    # qr_code = QRCode.objects.create(
    #     wallet=wallet,
    #     qr_data=data,  # Сохраняем строку с данными кошелька
    #     qr_image=base64.b64encode(img_bytes.getvalue()).decode()  # Сохраняем байты изображения QR-кода
    # )
    return img_bytes.getvalue()


async def get_photo_qr_code(wallet: Wallet) -> BufferedInputFile:
    qr_bytes = await generate_qr_code(wallet)
    photo = BufferedInputFile(qr_bytes, filename="qr_code.png")
    return photo


def parse_scanned_data(text: str) -> dict:
    data = {}

    # Извлекаем адрес кошелька
    wallet_address_match = re.search(r'Address: ([\w\d]+)', text)
    if wallet_address_match:
        wallet_address = wallet_address_match.group(1)
        data['wallet_address'] = wallet_address

    # Извлекаем имя кошелька
    wallet_name_match = re.search(r'Name: (.+)', text)
    if wallet_name_match:
        wallet_name = wallet_name_match.group(1)
        data['wallet_name'] = wallet_name

    # Извлекаем описание кошелька
    wallet_description_match = re.search(r'Description: (.+)', text)
    if wallet_description_match:
        wallet_description = wallet_description_match.group(1)
        data['wallet_description'] = wallet_description

    return data
