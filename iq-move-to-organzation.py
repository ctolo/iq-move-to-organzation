#!/usr/bin/python3
import requests

# ---------------------------------------------
iq_url = "http://localhost:8070"
auth = "admin:admin123"
default_tag = "Internal"
default_org = "Sandbox Organization"

# -------------------------------------------------
auth = auth.split(":")
iq_session = requests.Session()
iq_session.auth = requests.auth.HTTPBasicAuth(auth[0], auth[1])
add_tag, orgs, org_id, tag_id = {}, {}, "", ""
# -------------------------------------------------

# Getting all organizations.
url = f'{iq_url}/api/v2/organizations'
response = iq_session.get(url).json()
for org in response["organizations"]:
	# Will use the orgs object to lookup organizations by name later.
	orgs.update({ org["name"] : org["id"]})

	# For root org, look for the default tag (application category) 
	if org["id"] == "ROOT_ORGANIZATION_ID":
		for tag in org["tags"]:
			if tag["name"] == default_tag:
				tag_id = tag['id']
				print(f"Found default_tag ({default_tag}): {tag_id}")
				add_tag = {"tagId": tag_id }

# Stop if there is no default tag.
if not bool(add_tag):
	print(f"Did not find default_tag:{default_tag}")
	exit(1)

# Stop if there is no default org.
if default_org in orgs.keys():
	org_id = orgs[default_org]
	print(f"Found default_org ({default_org}): {org_id}")
else:
	print(f"Did not find default_org:{default_org}")
	exit(1)

#Looping through all applications
print(f"Checking for applications without tags ..")
url = f'{iq_url}/api/v2/applications'
response = iq_session.get(url).json()
for app in response["applications"]:

	# Focus on applications in the default org.
	if app["organizationId"] == org_id:
		app_name, app_id = app["name"], app['id']
		new_org = app_name[:3]
		print(f".app: {app_name}")

		# Checking for application tags (category) 
		# If app doesn't have any add the default tag
		if len(app["applicationTags"]) == 0:
			print(f".. adding tag to app: {app_name}")
			app["applicationTags"].append(add_tag)
			
			url = f"{iq_url}/api/v2/applications/{app_id}"
			result = iq_session.put(url, json=app)
			if result.status_code == requests.codes.ok:	
				print(f".. successful")
			else:
				print(f".. FAILED")

		# Checking for organization with the same prefix as app.
		# If orgs are found then move app to the new org. 
		if new_org in orgs.keys():
			new_org_id = orgs[new_org]
			print(f".. moving app to org ({new_org}): {new_org_id}")
			url = f"{iq_url}/api/v2/applications/{app_id}/move/organization/{new_org_id}"
			result = iq_session.post(url)
			if result.status_code == requests.codes.ok:	
				print(f".. successful")
			else:
				print(f".. FAILED")

print("== fin")
