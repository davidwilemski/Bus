#!/usr/bin/env python
import argparse
import re
import sys

from tornado import httpclient, ioloop

def end_loop():
    ioloop.IOLoop.instance().stop()


def get_max_width(table, i):
    return max([len(row[i]) for row in table])

def print_table(table):
    if table is None:
        print "Info for route " + args.route[0] + " is unavailable.";
        end_loop()
        return

    col_paddings = []
    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))
   
    print "\n\n", 
    print table[0][0].ljust(col_paddings[0] + 1),
    for i in range(1, len(table[0])):
        col = table[0][i].rjust(col_paddings[i] + 2)
        print col,
    

    print "\n" 
    print "-" * (sum(col_paddings) + 3 * len(col_paddings))

    table.pop(0)
    for row in table:
        print row[0].ljust(col_paddings[0] + 1),
        for i in range(1, len(row)):
            col = row[i].rjust(col_paddings[i] + 2)
            print col,
        
        print '\n'

    print '\n'
    end_loop()

def get_route_data(route, callback):
    # compose callback with parser
    # wanted to use this, but it is fully evaluated before I want:
    #cb = lambda x: callback(parse_route_data(x))

    def cb(x):
        data = parse_route_data(x)
        callback(data)
        

    # Get the routes
    http_client = httpclient.AsyncHTTPClient()
    r = http_client.fetch("http://mobile.aata.org/rideguide_m.asp?route=" + str(route), cb)

def parse_route_data(response):
    # parse them
    try:
        arr = response.body.split("<hr />")
        routes = [['', '', '', '', ''] for x in range(len(arr) - 1) ]
        routes[0] = ["Direction", "Arriving", "Location", "Next Stop", "Time"]


        # Regex to split the bus direction and time delay
        r = re.compile('(On time|[0-9]+ min ahead|[0-9]+ min behind)')


        for x in xrange(1, len(arr)-1):
            temp = arr[x].split("<br />")

            # strip bus number and space
            temp[0] = temp[0][4:]
        
            # Split the direction and time delay
            loc = r.split(temp[0])
            routes[x][0] = loc[0] 
            routes[x][1] = loc[1]

            # Strip the @ symbol
            routes[x][2] = temp[1][2:]

            # Split the arival time and next stop 
            routes[x][4] = temp[2][-5:].strip()
            routes[x][3] = temp[2][:-5].strip()

        return routes

    except:
        #raise
        return None


if __name__ == '__main__':
    # Get the route args
    parser = argparse.ArgumentParser(description='Display the current bus schedules')
    parser.add_argument('route', nargs=1, help='route you\'re trying to view')
    args = parser.parse_args()

    try:
        get_route_data(args.route[0].upper(), print_table)
        ioloop.IOLoop.instance().start()
    
    finally:
        exit()
