import gitlab
import yaml
import urllib3
urllib3.disable_warnings()

config_file = 'config/gitlab-bot.ini'

# private token or personal token authentication
try:
    gl = gitlab.Gitlab.from_config('my-server', [config_file])
except:
    print("Could not connect to gitlab-server")
    
# list all the projects
projects = gl.projects.list()
for project in projects:
    print(project.name)
