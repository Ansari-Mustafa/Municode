from Bot.Bot import AutoBot
import time
import Bot.constants as const

def run(search):
    with AutoBot() as test:
        test.open_url(const.base_url)       # Opens main URL
        test.select_state(const.state)      # Selects State
        test.select_county(const.county)    # Selects County
        time.sleep(10)
        test.search_bar(search)             # Search the term
        time.sleep(5) 
        test.get_top_results(const.top)
        

run("Minimum trees per lot")
#run("vegetation")
#run("trees allowed on lot")
#run("tree types")
#run("native")
#run("tree height")

time.sleep(5)
