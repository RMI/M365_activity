#Load SharePoint CSOM Assemblies
Add-Type -Path "C:\Program Files\Common Files\Microsoft Shared\Web Server Extensions\16\ISAPI\Microsoft.SharePoint.Client.dll"
Add-Type -Path "C:\Program Files\Common Files\Microsoft Shared\Web Server Extensions\16\ISAPI\Microsoft.SharePoint.Client.Runtime.dll"
Add-Type -Path "C:\Program Files\Common Files\microsoft shared\Web Server Extensions\16\ISAPI\Microsoft.SharePoint.Client.Taxonomy.dll"
 
#Function to recursively get all child terms from a Term
Function Get-SPOTerm([Microsoft.SharePoint.Client.Taxonomy.Term]$Term)
{
    Write-host $Term.Name
    #Get All child terms
    $ChildTerms = $Term.Terms
    $Ctx.Load($ChildTerms)
    $Ctx.ExecuteQuery()
 
    #Process all child terms
    Foreach ($ChildTerm in $ChildTerms)
    {
        $Indent = $Indent +"`t"
        Write-host $Indent -NoNewline
        Get-SPOTerm($ChildTerm)
    }
    $Indent = "`t"
}
 
#Parameters
$AdminCenterURL = "https://rockmtnins.sharepoint.com/sites/KnowledgeCatalog/_layouts/15/SiteAdmin.aspx#/termStoreAdminCenter"
$TermGroupName="Knowledge Management"
$TermsetName="Content Tags"
 
#Get Credentials to connect
$Cred= Get-Credential
  
#Setup the context
$Ctx = New-Object Microsoft.SharePoint.Client.ClientContext($AdminCenterURL)
$Ctx.Credentials = New-Object Microsoft.SharePoint.Client.SharePointOnlineCredentials($Cred.Username, $Cred.Password)
 
#Get the taxonomy session and termstore
$TaxonomySession = [Microsoft.SharePoint.Client.Taxonomy.TaxonomySession]::GetTaxonomySession($Ctx)
$TermStore =$TaxonomySession.GetDefaultSiteCollectionTermStore()
$Ctx.Load($TaxonomySession)
$Ctx.Load($TermStore)
  
#Get the Term Group   
$TermGroup = $TermStore.Groups.GetByName($TermGroupName)
$Ctx.Load($TermGroup)
  
#Get the termset
$TermSet = $TermGroup.TermSets.GetByName($TermSetName)
$Ctx.Load($TermSet)
$Ctx.ExecuteQuery()
 
#Get all terms
$TermColl=$TermSet.Terms
$Ctx.Load($TermColl)
$Ctx.ExecuteQuery()
 
# Loop through all the terms
Foreach($Term in $TermColl)
{
    #Get the terms recursively
    Get-SPOTerm($Term)
}


############33

#Config Variables
$AdminCenterURL = "https://rockmtnins.sharepoint.com/sites/KnowledgeCatalog/_layouts/15/SiteAdmin.aspx#/termStoreAdminCenter"
 
#Connect to PnP Online
Connect-PnPOnline -Url $AdminCenterURL -Credentials (Get-Credential)
 
#Get All Terms from a Term Set
Get-PnPTerm -TermSet "DealStage" -TermGroup "Deals Pipeline"


##################

#Parameters
$AdminCenterURL = "https://rockmtnins.sharepoint.com/sites/KnowledgeCatalog/_layouts/15/SiteAdmin.aspx#/termStoreAdminCenter"
 
#Connect to PnP Online
Connect-PnPOnline -Url $AdminCenterURL -Interactive
 
#Get All Terms from a Term Set
Get-PnPTerm -TermGroup "Knowledge Management" -TermSet "Content Tags" | Select Name | Export-Csv "c:\Users\ghoffman\OneDrive - RMI\01. Projects\Python_General\Terms.csv" -NoTypeInformation

