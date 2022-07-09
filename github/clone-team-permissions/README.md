# github-clone-team-permissions.py

### clone repository roles between teams in your GitHub organization

:warning: To use this script you need to have a `GH_TOKEN` environment variable set.  This contains a [developer
token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) 
that has `repo` scope, and belongs to an _organization admin_ user.   

Usage:
```
❯ ./github-clone-team-permissions.py -h
usage: github-clone-team-permissions.py [-h] org fromteam toteam

Find all repos for which a team has been granted an explicit access role, and grant a different team the same access. Requires a GH_TOKEN token in scope, which belongs to an organization admin, with
'repo' scope.

positional arguments:
  org         your organization
  fromteam    the source team name
  toteam      the team to which the permissions will be cloned

optional arguments:
  -h, --help  show this help message and exit
```

example:
```
❯ export GH_TOKEN=my-org-admin-token-with-repo-scope
❯ ./github-clone-team-permissions.py acmecorp team_a team_b

Hi Barry O'Neill (barryoneill), checking that you are an admin of the 'acmecorp' org..
team_a has access to 44 repos, filtering to explicitly set permissions..
The following explicit permissions are set for team_a:
 - repo1: admin
 - repo2: admin
 - repo3: pull
 - repo4: admin
 - repo5: push
 
Copy these repo permissions to team_b? (y/N) y
 - granting 'admin' permission on repo1 to team_b..
 - granting 'admin' permission on repo2 to team_b..
 - granting 'pull' permission on repo3 to team_b..
 - granting 'admin' permission on repo4 to team_b..
 - granting 'push' permission on repo5 to team_b..
 
Done!

Process finished with exit code 0  
```


