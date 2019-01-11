from gino import Gino

import settings

db = Gino()

import chat.models
import accounts.models
