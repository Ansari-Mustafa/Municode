from Bot.Bot import AutoBot
import time
import Bot.constants as const


with AutoBot() as test:
    test.open_url(const.base_url)       # Opens main URL
    test.save_states()
    test.save_cities()

       
time.sleep(1)
