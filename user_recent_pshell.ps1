
msgraph.graph_service_client
graph_client = GraphServiceClient(request_adapter)


result = await graph_client.me.people.get()


Import-Module Microsoft.Graph.People


Get-MgUserSharedInsight -UserId $userId


Find-MgGraphCommand -command Get-MgUser | Select -First 1 -ExpandProperty Permissions

Connect-MgGraph -Scopes "User.Read.All","Group.ReadWrite.All"
