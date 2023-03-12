"""
    All Salesforce metadata types
    "directoryName": "xmlName"
"""

# use XML name for types which need the folder
inside_Folder = ['Dashboard', 'Document', 'EmailTemplate', 'Report']
# requires names inside the file
inside_File = ['CustomLabels']
# if the type has child items, define child directory name and XML name
has_child_Items = {
                    'CustomObject': [{'fields': 'CustomField'},
                                     {'compactLayouts': 'CompactLayout'},
                                     {'webLinks': 'WebLink'},
                                     {'validationRules': 'ValidationRule'},
                                     {'recordTypes': 'RecordType'},
                                     {'listViews': 'ListView'},
                                     {'fieldSets': 'FieldSet'}
                                     ]
                    }

metadata_Types = {
    "applications": "CustomApplication",
    "appMenus": "AppMenu",
    "approvalProcesses": "ApprovalProcess",
    "assignmentRules": "AssignmentRules",
    "audience": "Audience",
    "aura": "AuraDefinitionBundle",
    "authproviders": "AuthProvider",
    "autoResponseRules": "AutoResponseRules",
    # Bots has two items - double check this later
    "bots": "Bot",
    "brandingSets": "BrandingSet",
    "certs": "Certificate",
    "classes": "ApexClass",
    "cleanDataServices": "CleanDataService",
    "communities": "Community",
    "components": "ApexComponent",
    "connectedApps": "ConnectedApp",
    "contentassets": "ContentAsset",
    "corsWhitelistOrigins": "CorsWhitelistOrigin",
    "customApplicationComponents": "CustomApplicationComponent",
    "customMetadata": "CustomMetadata",
    "customPermissions": "CustomPermission",
    "dashboards": "Dashboard",
    "delegateGroups": "DelegateGroup",
    "documents": "Document",
    "duplicateRules": "DuplicateRule",
    "email": "EmailTemplate",
    "emailservices": "EmailServicesFunction",
    "escalationrules": "EscalationRules",
    "experiences": "ExperienceBundle",
    "feedFilters": "CustomFeedFilter",
    "flexipages": "FlexiPage",
    "flowDefinitions": "FlowDefinition",
    "flows": "Flow",
    "globalValueSets": "GlobalValueSet",
    "globalValueSetTranslations": "GlobalValueSetTranslation",
    "groups": "Group",
    "homePageComponents": "HomePageComponent",
    "homePageLayouts": "HomePageLayout",
    "installedPackages": "InstalledPackage",
    "labels": "CustomLabels",
    "layouts": "Layout",
    "LeadConvertSettings": "LeadConvertSettings",
    "letterhead": "Letterhead",
    "lightningExperienceThemes": "LightningExperienceTheme",
    "liveChatAgentConfigs": "LiveChatAgentConfig",
    "liveChatDeployments": "LiveChatDeployment",
    "lwc": "LightningComponentBundle",
    "matchingRules": "MatchingRule",
    "messageChannels": "LightningMessageChannel",
    "namedCredentials": "NamedCredential",
    "navigationMenus": "NavigationMenu",
    "networkBranding": "NetworkBranding",
    "networks": "Network",
    "objectTranslations": "CustomObjectTranslation",
    "objects": "CustomObject",
    "pages": "ApexPage",
    "pathAssistants": "PathAssistant",
    "permissionsets": "PermissionSet",
    "platformEventChannelMembers": "PlatformEventChannelMember",
    "presenceUserConfigs": "PresenceUserConfig",
    "profilePasswordPolicies": "ProfilePasswordPolicy",
    "profileSessionSettings": "ProfileSessionSetting",
    "profiles": "Profile",
    "queueRoutingConfigs": "QueueRoutingConfig",
    "queues": "Queue",
    "quickActions": "QuickAction",
    "reportTypes": "ReportType",
    "reports": "Report",
    "remoteSiteSettings":  "RemoteSiteSetting",
    "prompts":  "Prompt",
    "roles": "Role",
    "samlssoconfigs": "SamlSsoConfig",
    "scontrols": "Scontrol",
    "settings": "Settings",
    "sharingRules": "sharingRules",
    "sharingSets": "SharingRules",
    "siteDotComSites": "SiteDotCom",
    "sites": "CustomSite",
    "skills": "Skill",
    "standardValueSets": "StandardValueSet",
    "staticresources": "StaticResource",
    "tabs": "CustomTab",
    "territory2Models": "Territory2Model",
    "territory2Types": "Territory2Type",
    "topicsForObjects": "TopicsForObjects",
    "triggers": "ApexTrigger",
    "wave": "wave",
    "webLinks": "WebLink",
    "workflows": "Workflow"
}
