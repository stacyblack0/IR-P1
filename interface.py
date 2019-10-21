import curses
import traceback
from random import randint

from query_suggestions import QuerySuggest

# Takes a user's (incomplete) query, and returns a list of query suggestions.
def fetch_suggestions(partial_query):

    # join character list into string
    partial_query = ''.join(partial_query)

    # remove any extra spaces from query
    partial_query = partial_query.strip()

    # adding random number for testing
    test_id1 = str(randint(0, 999999))
    test_id2 = str(randint(0, 999999))
    test_id3 = str(randint(0, 999999))

    # ret = [partial_query + ' ' + test_id1, partial_query + ' ' + test_id2, partial_query + ' ' + test_id3]
    ret = query_suggest.get_suggestions(partial_query)

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
def do_suggest(q):

    clear_results()

    # get suggestions and display them
    suggestions = fetch_suggestions(q)
    for i, doc in enumerate(suggestions):
        doc_str = str(i+1) + ' ' + doc
        stdscr.addstr(query_y+2+i, query_x, doc_str)
    
    reset_query_cursor()

    return suggestions

# handle pressing enter, which starts a search
def do_search_result(q):

    clear_results()

    # stdscr.addstr(query_y+2, query_x, 'top search results:')

    # get search results and display them
    search_results = fetch_search_results(q)
    for i, doc in enumerate(search_results):
        doc_str = str(i+1) + ' ' + doc
        stdscr.addstr(query_y+2+i, query_x, doc_str)
    
    stdscr.addstr(query_y, query_x, ' ' * len(q))

    return search_results

# handle pressing backspace
def do_backspace():
    if len(query) > 0:
        stdscr.addstr(query_y, query_x+len(query)-1, ' ')
        del query[-1]
        reset_query_cursor()

# if a user uses the arrow keys, handle selection of suggestions/results
def do_select(arrow):

    position = 1
    max_position = 3
    result_selected = False
    result_num = 0
    stdscr.addstr(query_y+1+position, query_x, str(position))

    # while loop doesn't exit until user hits enter or moves cursor back to query line
    while position > 0:

        arrow = stdscr.getch()

        # up
        if arrow == 65:
            position -= 1
        # down
        elif arrow == 66:
            if (position+1) <= max_position:
                position += 1
        # enter
        elif arrow == 10:
            result_selected = True
            result_num = position
            position = 0

        if position == 0:
            reset_query_cursor()
            break
        else:
            stdscr.addstr(query_y+1+position, query_x, str(position))

    return result_selected, result_num

def do_fetch_document(doc_id):
    # TODO: print document to screen somehow
    stdscr.addstr(query_y+5, query_x, "fetched document " + str(doc_id))
    reset_query_cursor()
    i=1

try:

    # initialize query suggestions class
    query_suggest = QuerySuggest()

    # initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    # stdscr.keypad(1)

    # start point of query entry on screen
    query_x = 2
    query_y = 2

    # list of characters that make up the query
    query = []

    # init_color()
    init_ui()

    # whether or not suggestions/results have been generated
    has_suggestions = False
    has_results = False
    results_list = [] # TODO: make this a dict?

    while True: 

        ch = stdscr.getch()

        # don't add non-alphanumeric characters, like enter and backspace, to the query, or arrow keys or square brackets
        if ch in range(32, 127) and ch not in range(65, 69) and ch != 91 and ch != 93:
            query.append(chr(ch))

        # print query so far to screen
        stdscr.addstr(query_y, query_x, ''.join(query))

        # user presses down key to select suggestion/result
        if ch == 66 and (has_suggestions == True or has_results == True):

            has_selected, selected_num = do_select(ch)

            if has_selected == True:
                if has_suggestions == True:
                    results_dict = do_search_result(results_list[selected_num-1])
                    # can't get these to work in function scope
                    query = []
                    reset_query_cursor()
                    has_results = True
                    has_suggestions = False
                elif has_results == True:
                    do_fetch_document(selected_num)
                    has_results = False
        
        # if hitting space, retrieve suggestions, except if space already pressed
        if chr(ch) == ' ' and query[len(query) - 2] != ' ':
            results_list = do_suggest(query)
            has_suggestions = True
        # if hitting enter, launch search and clear query line
        elif ch == 10 and len(query) > 0:
            results_list = do_search_result(query)
            # can't get these to work in function scope
            query = []
            reset_query_cursor()
            has_results = True
            has_suggestions = False

        # if pressing backspace, remove character from entry list of characters
        elif ch == 127:
            do_backspace()

except:
    traceback.print_exc()  # print trace back log of the error

# cleanup on exit    
finally:
    # stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
