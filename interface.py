import curses
import traceback
from random import randint

# Takes a user's (incomplete) query, and returns a list of document suggestions.
def fetch_suggestions(partial_query):

    # join character list into string
    partial_query = ''.join(partial_query)

    # remove any extra spaces from query
    partial_query = partial_query.strip()

    # adding random number for testing
    test_id1 = str(randint(0, 999999))
    test_id2 = str(randint(0, 999999))
    test_id3 = str(randint(0, 999999))
    # TODO: get top suggestions from wikipedia corpus, which will be returned
    ret = [partial_query + ' ' + test_id1, partial_query + ' ' + test_id2, partial_query + ' ' + test_id3]

    return ret

# Takes a user's (full) query, and returns a list of document search results.
def fetch_search_results(full_query):

    # join character list into string
    full_query = ''.join(full_query)

    # remove any extra spaces from query
    full_query = full_query.strip()

    # adding random number for testing
    test_id1 = str(randint(0, 999999))
    test_id2 = str(randint(0, 999999))
    test_id3 = str(randint(0, 999999))
    # TODO: get top suggestions from wikipedia corpus, which will be returned
    ret = [full_query + ' ' + test_id1, full_query + ' ' + test_id2, full_query + ' ' + test_id3]

    return ret

# clears suggestions and search results (everything after cursor)
def clear_results():
    stdscr.clrtobot()
    init_ui()

# move cursor back to query line
def reset_query_cursor():
    stdscr.move(query_y, query_x + len(query))

# set up border and caption
def init_ui():
    # add border
    stdscr.border(0)
    # print message to screen
    stdscr.addstr(0, 1, 'Enter a search term. Do it.')
    # move cursor to query line
    reset_query_cursor()

# use custom colors in the interface
def init_color():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

# handle pressing space, which starts providing suggestions
def do_suggest():

    clear_results()

    # get suggestions and display them
    suggestions = fetch_suggestions(query)
    for i, doc in enumerate(suggestions):
        doc_str = str(i+1) + ' ' + doc
        stdscr.addstr(query_y+2+i, query_x, doc_str)
    
    reset_query_cursor()

# handle pressing enter, which starts a search
def do_search_result():

    clear_results()

    stdscr.addstr(query_y+2, query_x, 'top search results:')

    # get search results and display them
    search_results = fetch_search_results(query)
    for i, doc in enumerate(search_results, start=1):
        doc_str = str(i) + ' ' + doc
        stdscr.addstr(query_y+2+i, query_x, doc_str)
    
    stdscr.addstr(query_y, query_x, ' ' * len(query))

# handle pressing backspace
def do_backspace():
    if len(query) > 0:
        stdscr.addstr(query_y, query_x+len(query)-1, ' ')
        del query[-1]
        reset_query_cursor()

# if a user uses the arrow keys, handle selection of suggestions/results
def do_select():

    position = 1
    max_position = 3
    while position > 0:
        # TODO: don't exit until cursor goes back up to the query line?
        # up
        if ch == 65:
            stdscr.addstr(7, 7, ' ', curses.color_pair(2))
            # reset_query_cursor()
        # down
        if ch == 66:
            stdscr.addstr(7, 7, 'test2')
        # right
        if ch == 67:
            stdscr.addstr(7, 7, 'test3')
        # left
        if ch == 68:
            stdscr.addstr(7, 7, 'test4')

try:

    # initialize curses
    stdscr = curses.initscr()
    curses.noecho()

    # start point of query entry on screen
    query_x = 2
    query_y = 2

    # list of characters that make up the query
    query = []

    init_color()
    init_ui()

    while True: 

        ch = stdscr.getch()

        # don't add non-alphanumeric characters, like enter and backspace, to the query
        if ch in range(32, 127) and ch not in range(65, 69) and ch != 91 and ch != 93:
        # if ch != 10 and ch != 127:
            query.append(chr(ch))
        # stdscr.addstr(9, 6, str(ch))

        # print query so far to screen
        stdscr.addstr(query_y, query_x, ''.join(query))

        # user presses arrow keys
        if ch in range(65, 69):
            do_select()
        
        # if hitting space, retrieve suggestions, except if space already pressed
        if chr(ch) == ' ' and query[len(query) - 2] != ' ':
            do_suggest()
        # if hitting enter, launch search and clear query line
        elif ch == 10:
            do_search_result()
            # can't get these to work in function scope
            query = []
            reset_query_cursor()

        # if pressing backspace, remove character from entry list of characters
        elif ch == 127:
            do_backspace()

except:
    traceback.print_exc()  # print trace back log of the error

# cleanup on exit    
finally:
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
