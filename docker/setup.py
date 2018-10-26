from setuptools import setup

setup(name='gitlab-bot',
      version='0.1',
      description='Python bot for automating regular mandraulic Gitlab tasks',
      url='https://github.com/d3ll10tt/gitlab-bot',
      author='d3ll10tt',
      license='MIT',
      packages=['gitlab-bot'],
      install_requires=[
          'python-gitlab==1.4.0',
          'pyyaml',
      ],
      zip_safe=False)