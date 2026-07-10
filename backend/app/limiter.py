"""
Окремий файл лише для об'єкта Limiter (rate limiting).

Винесено з main.py в окремий модуль навмисно: якщо тримати limiter
прямо в main.py, а роутери (auth_router.py) імпортувати його звідти —
вийде циклічний імпорт (main.py імпортує роутери, роутери імпортують
limiter з main.py). Тут — нейтральне місце, яке не залежить ні від
main.py, ні від роутерів, тож обидва можуть імпортувати звідси без проблем.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
