from dotenv import dotenv_values
import sys

ebOptions = {
    'min-instances': '1',
    'max-instances': '3',
    'instance_profile': 'aws-elasticbeanstalk-ec2-role',
    'service-role': 'aws-elasticbeanstalk-service-role',
    'elb-type': 'application',
    'instance-types':'t3.micro',
    'keyname':'aws-eb'
}

try:
    CONFIGURATION_FILE = sys.argv[1]
    HOSTNAME = sys.argv[2]
except:
    print('ERROR: filename missing\npython ebCreate.py environment hostname')
    exit()
config = dotenv_values(CONFIGURATION_FILE)

hostname = f'{HOSTNAME}.{config["AWS_DEFAULT_REGION"]}.elasticbeanstalk.com'


opt = []
for k, v in config.items():
    opt.append(f'{k}={v}')
opt.append('PYTHONUNBUFFERED=1')
ebOptions['cname'] = HOSTNAME
ebOptions['envvars'] = '"%s"' % ','.join(opt)

opt = []
for k, v in ebOptions.items():
    opt.append(f'--{k} {v}')

print(f'eb create {HOSTNAME} %s ' % ' '.join(opt))
