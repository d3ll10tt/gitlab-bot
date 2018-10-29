import os
import time
import re
from slackclient import SlackClient
from apscheduler.schedulers.background import BackgroundScheduler
import gitlab
import urllib3
urllib3.disable_warnings()

project_id = os.environ.get('PROJECT_ID')
bot_token = os.environ.get('BOT_TOKEN')
gitlab_server = os.environ.get('GIT_SERVER')
git_token = os.environ.get('GIT_TOKEN')

# instantiate Slack client
slack_client = SlackClient(bot_token)
# TNDbot's user and user ID in Slack: id value is assigned after the bot starts up
TNDbot_id = None
TNDbot_user = 'tnd-merge-bot'

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
CMD_MR_LIST_OPEN = ("list open mr", "list open mrs")
CMD_MR_LIST_UNASSIGNED = ("list unassigned mr", "list unassigned mrs")
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# instantiate gitlab connection
try:
    gl = gitlab.Gitlab(gitlab_server, private_token=git_token, ssl_verify=False, timeout=10, api_version='3')
    # Get target project
    project = gl.projects.get(project_id)
except:
    print("Could not connect to gitlab-server")




def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == TNDbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """


    # Finds and executes the given command, filling in response
    response = None
    if command.lower().startswith(("hi","hello")):
        response = "Hi there. What can I help you with today?"
    elif command.lower().startswith(CMD_MR_LIST_OPEN):

        merge_requests = project.mergerequests.list(state='opened', order_by='created_at')
        response = "Here is a list of current open merge requests:\n\n"
        for mr in merge_requests:
            response = response + mr.web_url + "\n" \
                        + "Target: " + mr.target_branch \
                        + "\nTitle: \"" + mr.title + "\"" \
                        + "\nAuthor: " + mr.author.name
            if mr.assignee != None:
             response = response + "\nAssigned for review/approval to: " + mr.assignee.name
            else:
             response = response + "\nAssigned for review/approval to: No Assignee!"
            response = response + "\n\n"

    elif command.lower().startswith(CMD_MR_LIST_UNASSIGNED):

        merge_requests = project.mergerequests.list(state='opened', order_by='created_at')
        response = "Here is a list of open merge requests with no assignee:\n\n"
        for mr in merge_requests:
            if mr.assignee == None:
                response = response + mr.web_url + "\n" \
                           + "Target: " + mr.target_branch \
                           + "\nTitle: \"" + mr.title + "\"" \
                           + "\nAuthor: " + mr.author.name \
                           + "\n\n"

    else:
        # Default response is help text for the user
        default_response = "Not sure what you mean..."

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        as_user=TNDbot_user,
        text=response or default_response
    )

def test_msg():

    print("In test_msg")

    slack_client.api_call(
        "chat.postMessage",
        channel='jenkins-test',
        as_user=TNDbot_user,
        text="APSScheduler cron message every minute"
    )

if __name__ == "__main__":

    # Initialise scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(test_msg, 'cron', minute='*')
    scheduler.start()

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        TNDbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")