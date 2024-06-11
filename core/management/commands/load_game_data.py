# your_app/management/commands/load_google_sheet_data.py

import os
import json
import gspread
from django.core.management.base import BaseCommand
import gspread
from google.oauth2.service_account import Credentials

from Common.DataLoader import Constant, DataLoader, GOACharacter, GOACard

game_data = None

class GameData():
    def __init__(self, characters, cards, constants):
        self.characters = characters
        self.cards = cards
        self.constatns = constants

class Command(BaseCommand):
    help = 'Load data from Google Sheets into Django'

    def handle(self, *args, **options):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file('goawebsocket-2c1d9a4aecc4.json', scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open('GOA Websocket Datasheet')

        constants = DataLoader(sheet, "Constants", Constant)
        cards = DataLoader(sheet, "GOACards", GOACard)
        characters = DataLoader(sheet, "GOACharacters", GOACharacter)
        
        
        global game_data
        game_data = GameData(characters, cards, constants)