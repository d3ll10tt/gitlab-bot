import gitlab
import yaml


my_dict = yaml.safe_load(open('config/gitlab-bot-config.yaml'))
print(my_dict)
