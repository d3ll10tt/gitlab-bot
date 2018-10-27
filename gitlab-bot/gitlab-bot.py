import gitlab
import os
from slackclient import SlackClient
import urllib3
urllib3.disable_warnings()

config_file = 'config/gitlab-bot.ini'
project_id = os.environ.get('PROJECT-ID')

# instantiate Slack client
slack_client = SlackClient(os.environ.get('BOT-TOKEN'))

# instantiate gitlab connection
try:
    gl = gitlab.Gitlab.from_config('my-server', [config_file])
except:
    print("Could not connect to gitlab-server")
    
# list all the projects
project = gl.projects.get(project_id)


merge_requests = project.mergerequests.list(state='opened', order_by='created_at')

# find MR with no Assignee

for mr in merge_requests:
    if mr.assignee == None:
        print("No assignee:", mr.iid, mr.title, mr.author.name, sep=" ")
        bot_msg = "Merge request " + str(mr.iid) + " \"" + mr.title + "\"" + " has no assignee set. " +  mr.author.name + " - Please assign a reviewer for this MR to stop these messages."

        slack_client.api_call(
            "chat.postMessage",
            channel='slack-testing',
            text=bot_msg
        )
        slack_client.api_call(
            "chat.postMessage",
            channel='Dave',
            text=bot_msg
        )


