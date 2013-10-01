#!/usr/bin/python
import requests
import fbconsole
import re
import curses
import os

# facebook app config stuff
fbconsole.APP_ID = os.environ['FBBOTAPPID']
fbconsole.AUTH_SCOPE = ['publish_stream','publish_actions','user_groups']
APP_SECRET = os.environ['FBBOTAPPSECRET']
GROUP_ID = os.environ['FBBOTGROUPID']


# last post on group
LAST_POST_ID = None

opened = """
                              THE WHITE HAT LAB IS

     OOOOOOOOO     PPPPPPPPPPPPPPPPP   EEEEEEEEEEEEEEEEEEEEEENNNNNNNN        NNNNNNNN
   OO:::::::::OO   P::::::::::::::::P  E::::::::::::::::::::EN:::::::N       N::::::N
 OO:::::::::::::OO P::::::PPPPPP:::::P E::::::::::::::::::::EN::::::::N      N::::::N
O:::::::OOO:::::::OPP:::::P     P:::::PEE::::::EEEEEEEEE::::EN:::::::::N     N::::::N
O::::::O   O::::::O  P::::P     P:::::P  E:::::E       EEEEEEN::::::::::N    N::::::N
O:::::O     O:::::O  P::::P     P:::::P  E:::::E             N:::::::::::N   N::::::N
O:::::O     O:::::O  P::::PPPPPP:::::P   E::::::EEEEEEEEEE   N:::::::N::::N  N::::::N
O:::::O     O:::::O  P:::::::::::::PP    E:::::::::::::::E   N::::::N N::::N N::::::N
O:::::O     O:::::O  P::::PPPPPPPPP      E:::::::::::::::E   N::::::N  N::::N:::::::N
O:::::O     O:::::O  P::::P              E::::::EEEEEEEEEE   N::::::N   N:::::::::::N
O:::::O     O:::::O  P::::P              E:::::E             N::::::N    N::::::::::N
O::::::O   O::::::O  P::::P              E:::::E       EEEEEEN::::::N     N:::::::::N
O:::::::OOO:::::::OPP::::::PP          EE::::::EEEEEEEE:::::EN::::::N      N::::::::N
 OO:::::::::::::OO P::::::::P          E::::::::::::::::::::EN::::::N       N:::::::N
   OO:::::::::OO   P::::::::P          E::::::::::::::::::::EN::::::N        N::::::N
     OOOOOOOOO     PPPPPPPPPP          EEEEEEEEEEEEEEEEEEEEEENNNNNNNN         NNNNNNN

                            Press Any Key To Close
"""

closed = """
                                                THE WHITE HAT LAB IS

        CCCCCCCCCCCCCLLLLLLLLLLL                  OOOOOOOOO        SSSSSSSSSSSSSSS EEEEEEEEEEEEEEEEEEEEEEDDDDDDDDDDDDD
     CCC::::::::::::CL:::::::::L                OO:::::::::OO    SS:::::::::::::::SE::::::::::::::::::::ED::::::::::::DDD
   CC:::::::::::::::CL:::::::::L              OO:::::::::::::OO S:::::SSSSSS::::::SE::::::::::::::::::::ED:::::::::::::::DD
  C:::::CCCCCCCC::::CLL:::::::LL             O:::::::OOO:::::::OS:::::S     SSSSSSSEE::::::EEEEEEEEE::::EDDD:::::DDDDD:::::D
 C:::::C       CCCCCC  L:::::L               O::::::O   O::::::OS:::::S              E:::::E       EEEEEE  D:::::D    D:::::D
C:::::C                L:::::L               O:::::O     O:::::OS:::::S              E:::::E               D:::::D     D:::::D
C:::::C                L:::::L               O:::::O     O:::::O S::::SSSS           E::::::EEEEEEEEEE     D:::::D     D:::::D
C:::::C                L:::::L               O:::::O     O:::::O  SS::::::SSSSS      E:::::::::::::::E     D:::::D     D:::::D
C:::::C                L:::::L               O:::::O     O:::::O    SSS::::::::SS    E:::::::::::::::E     D:::::D     D:::::D
C:::::C                L:::::L               O:::::O     O:::::O       SSSSSS::::S   E::::::EEEEEEEEEE     D:::::D     D:::::D
C:::::C                L:::::L               O:::::O     O:::::O            S:::::S  E:::::E               D:::::D     D:::::D
 C:::::C       CCCCCC  L:::::L         LLLLLLO::::::O   O::::::O            S:::::S  E:::::E       EEEEEE  D:::::D    D:::::D
  C:::::CCCCCCCC::::CLL:::::::LLLLLLLLL:::::LO:::::::OOO:::::::OSSSSSSS     S:::::SEE::::::EEEEEEEE:::::EDDD:::::DDDDD:::::D
   CC:::::::::::::::CL::::::::::::::::::::::L OO:::::::::::::OO S::::::SSSSSS:::::SE::::::::::::::::::::ED:::::::::::::::DD
     CCC::::::::::::CL::::::::::::::::::::::L   OO:::::::::OO   S:::::::::::::::SS E::::::::::::::::::::ED::::::::::::DDD
        CCCCCCCCCCCCCLLLLLLLLLLLLLLLLLLLLLLLL     OOOOOOOOO      SSSSSSSSSSSSSSS   EEEEEEEEEEEEEEEEEEEEEEDDDDDDDDDDDDD 

                                                Press Any Key To Open

"""

please_wait = """
   ___ _                       __    __      _ _         
  / _ \ | ___  __ _ ___  ___  / / /\ \ \__ _(_) |_       
 / /_)/ |/ _ \/ _` / __|/ _ \ \ \/  \/ / _` | | __|      
/ ___/| |  __/ (_| \__ \  __/  \  /\  / (_| | | |_ _ _ _ 
\/    |_|\___|\__,_|___/\___|   \/  \/ \__,_|_|\__(_|_|_)

"""

def authenticate():
    """Authenticate with facebook"""

    global APP_SECRET

    # get temp access token
    fbconsole.authenticate()

    # get longer access token
    params = {"grant_type":"fb_exchange_token",
            "client_id":fbconsole.APP_ID,
            "client_secret":APP_SECRET,
            "fb_exchange_token":fbconsole.ACCESS_TOKEN
            }
    post_resp = requests.post(url="https://graph.facebook.com/oauth/access_token",data=params)
    new_access_token = re.search(r'access_token=(.*)&',post_resp.text).groups()[0]
    fbconsole.ACCESS_TOKEN = new_access_token

def post_status(message):
    """Delete the old status then post a new one."""

    global LAST_POST_ID
    global GROUP_ID

    # check if logged in
    try:
        fbconsole.get("/me")
    except:
        authenticate()

    # delete the old status
    if LAST_POST_ID is not None:
        fbconsole.delete("/"+LAST_POST_ID)

    #make new status
    post = fbconsole.post("/" + GROUP_ID + "/feed",{"message":message})
    LAST_POST_ID = post['id']


def main():
   is_open = True
   stdscr = curses.initscr()
   curses.cbreak()
   curses.noecho()
   stdscr.keypad(1)
   key = ''
   authenticate()

   while 1:
      key = stdscr.getch()
      stdscr.clear()
      if is_open:
         stdscr.addstr(5,33,please_wait, curses.A_BLINK)
         stdscr.refresh()
         stdscr.addstr(5,33,closed, curses.A_BLINK)
         post_status("Lab is Closed :(")
      else:
         stdscr.addstr(5,33,please_wait, curses.A_BLINK)
         stdscr.refresh()
         stdscr.addstr(5,33,opened, curses.A_BLINK)
         post_status("Lab is Open :)")
      is_open = not is_open

if __name__ == "__main__":
   main()
