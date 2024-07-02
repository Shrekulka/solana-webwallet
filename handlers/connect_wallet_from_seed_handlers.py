# solana_wallet_telegram_bot/handlers/connect_wallet_handlers.py

import traceback

import mnemonic
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
########### django #########
from django.contrib.auth import get_user_model
# from sqlalchemy import select
from solders.keypair import Keypair

from applications.wallet.models import Wallet
# from database.database import get_db
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description, is_valid_wallet_seed_phrase


# Django
########################################################################################################################
# @sync_to_async
# def get_user(telegram_id):
#     User = get_user_model()
#     user = User.objects.filter(telegram_id=telegram_id).first()
#     return user
#
#
# @sync_to_async
# def create_wallet(user, name, description, wallet_address, solana_derivation_path):
#     wallet = Wallet.objects.create(
#         wallet_address=wallet_address,
#         name=name,
#         description=description,
#         solana_derivation_path=solana_derivation_path,
#     )
#     if wallet:
#         wallet.user.set([user])
#         user.last_solana_derivation_path = solana_derivation_path
#         user.save()
#     return wallet
########################################################################################################################

# Telegram
########################################################################################################################
# Инициализируем роутер уровня модуля
connect_wallet_from_seed_router: Router = Router()
