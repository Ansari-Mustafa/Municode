import time
from WebBot.Bot.Bot import AutoBot
import WebBot.Bot.constants as const
from selenium.common.exceptions import NoSuchElementException

def Automation(selected_state, selected_city, search_terms):
    try:
        with AutoBot() as ai:
            ai.open_url(const.base_url)     
            ai.select_state(selected_state)     
            ai.select_county(selected_city)    
            time.sleep(10)
            for i in range(len(search_terms)):
                ai.search_bar(search_terms[i])
                time.sleep(5)
                ai.get_top_results(3)

    except NoSuchElementException:
        print("Web AI Error!")
