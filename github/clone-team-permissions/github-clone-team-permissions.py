#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List, Tuple

from ghapi.all import GhApi, paged


# Given 'fromteam' and 'toteam' command line arguments, find all repos where 'fromteam' has been granted explicit
# permissions (as seen in the 'Manage Access' settings page in a repo), and grant the same permissions
# to 'toteam'.
#
# This script requires GH_TOKEN to be set in the environment.  Invoke clone_permissions.py --help for info.
#
# 2021 @barryoneill for https://github.com/ModaOperandi/moda-utils

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Find all repos for which a team has been granted an explicit access role, '
                    'and grant a different team the same access.  Requires a GH_TOKEN token in scope, '
                    'which belongs to an organization admin, with \'repo\' scope.')
    parser.add_argument('org', metavar='org', type=str, help='your organization')
    parser.add_argument('fromteam', metavar='fromteam', type=str, help='the source team name')
    parser.add_argument('toteam', metavar='toteam', type=str, help='the team to which the permissions will be cloned')
    return parser.parse_args()


def initialize_github_api(org) -> GhApi:
    api_token = os.getenv('GH_TOKEN')
    if api_token is None:
        sys.exit("Missing 'GH_TOKEN' environment variable.")

    api = GhApi(token=api_token)

    me = api.users.get_authenticated()
    print(f'Hi {me.name} ({me.login}), checking that you are an admin of the \'{org}\' org..')

    my_role = api.orgs.get_membership_for_user(org, me.login).role
    if api.orgs.get_membership_for_user(org, me.login).role != 'admin':
        sys.exit(f'Sorry, this script needs to be run with admin privileges (yours is: {my_role})')

    return api


def load_all_teams(api, org):
    """query the full list of the organization's teams"""
    pages = paged(api.teams.list, org=org, per_page=100)
    all_teams = [team for page in pages for team in page]
    return all_teams


def validate_team(teams, target):
    """verify that the provided team exists, otherwise exit"""
    team = next((team for team in teams if team.slug == target), None)
    if not team:
        sys.exit(f'No team called "{target}" in {[t.slug for t in teams]}')
    return team


def load_direct_team_repo_access(api, org, from_team) -> List[Tuple[str, str]]:
    """Get a list of (team, permission) tuples where each entry represents an explicit assignment that team
    has to a particular repo (as seen in the 'Manage Access' settings page in a repo).  """
    # first, find all repos to which this team has any access
    repo_pages = paged(api.teams.list_repos_in_org, org=org, team_slug=from_team.slug, per_page=100)
    accessible_repos = [repo for page in repo_pages for repo in page]

    print(f'{from_team.slug} has access to {len(accessible_repos)} repos, filtering to explicitly set permissions..')

    # get the details of the explicit assignment of this team to this repo, if there is one
    def get_explicit_assignment(repo) -> str:
        team_pages = paged(api.repos.list_teams, owner=org, repo=repo.name, per_page=100)
        teams_for_repo = [team for page in team_pages for team in page]

        return next((t.permission for t in teams_for_repo if t.slug == from_team.slug), None)

    all_assignments = list(map(lambda r: (r.name, get_explicit_assignment(r)), accessible_repos))
    res = list(filter(lambda a: a[1] is not None, all_assignments))

    print(f'The following explicit permissions are set for {from_team.slug}:')
    for (repo_name, permission) in res:
        print(f' - {repo_name}: {permission}')

    return res


def grant_access_to_team(api, org, to_team, repos_with_roles) -> None:
    for (repo_name, permission) in repos_with_roles:
        print(f' - granting \'{permission}\' permission on {repo_name} to {to_team.slug}..')
        api.teams.add_or_update_repo_permissions_in_org(org, to_team.slug, org, repo_name, permission)


def main() -> int:
    args = parse_args()
    api = initialize_github_api(args.org)

    teams = load_all_teams(api, args.org)
    from_team = validate_team(teams, args.fromteam)
    to_team = validate_team(teams, args.toteam)

    direct_repo_roles = load_direct_team_repo_access(api, args.org, from_team)

    if input("%s (y/N) " % f'\nCopy these repo permissions to {to_team.slug}?').lower() not in ('y', 'yes'):
        sys.exit('Exited with no changes')

    grant_access_to_team(api, args.org, to_team, direct_repo_roles)

    print('\nDone!')

    return 0


if __name__ == '__main__':
    sys.exit(main())
