import json
import boto3
import os

codecommit = boto3.client('codecommit')

def lambda_handler(event, context):
    repositories_list = list_codecommit_repositories()
    repositories_with_approvalrules_list = list_repositories_with_approvalrules()
    return difference_between_lists(repositories_list, repositories_with_approvalrules_list)

#Obtain all the reposities from AWS CodeCommit
def list_codecommit_repositories():
    repositories = []
    clean_repositories = []
    response = codecommit.list_repositories()
    if('repositories' in response and response['repositories'] != []):
        repositories.append(response['repositories'])
        while 'nextToken' in response and response['nextToken'].strip() != '':
            response = codecommit.list_repositories(nextToken=response['nextToken'])
            repositories.append(response['repositories'])
            
    for repository in repositories:
        for rep in repository:
            if('repositoryName' in rep):
                clean_repositories.append(rep['repositoryName'])
    return clean_repositories
  
#Obtain all approval rule templates  
def list_approval_rules():
    approval_rules = []
    response = codecommit.list_approval_rule_templates()
    approval_rules.append(response['approvalRuleTemplateNames'])
    if('repositories' in response and response['approvalRuleTemplateNames'] != []):
        while 'nextToken' in response and response['nextToken'].strip() != '':
            response = codecommit.list_approval_rule_templates(nextToken=response['nextToken'])
            approval_rules.append(response['approvalRuleTemplateNames'])
    return approval_rules


#Obtain all the reposities that have an approval rule assigned
def list_repositories_with_approvalrules():
    repositories = []
    repo_name = []
    approval_rules = list_approval_rules()
    for approval_rule in approval_rules:
        for app in approval_rule:
            response = codecommit.response = codecommit.list_repositories_for_approval_rule_template(
                approvalRuleTemplateName=app
            )
            for repo in response['repositoryNames']:
                repositories.append(repo)
            
            if('repositories' in response and response['repositoryNames'] != []):
                while 'nextToken' in response and response['nextToken'].strip() != '':
                    response = codecommit.list_repositories_for_approval_rule_template(
                        approvalRuleTemplateName=app,
                        nextToken=response['nextToken']
                    )
                    for repo in response['repositoryNames']:
                        repositories.append(repo)
    return repositories

# Find differences between all the repositories and the repositories with an approval rule assigned
def difference_between_lists(li1, li2):
    # Eliminate duplicates
    li1_clean = list(dict.fromkeys(li1))
    li2_clean = list(dict.fromkeys(li2))
    
    #Difference between two lists
    return list(set(li1) - set(li2))