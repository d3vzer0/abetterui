from azure.identity import DefaultAzureCredential
import azure.mgmt.resourcegraph as resourcegraph
from msrestazure import azure_cloud
import pandas as pd
import requests


class Watchlist:
    def __init__(self, content):
        self.content = content
    
    def __repr__(self):
        return self.content

    @property
    def as_dataframe(self):
        flat_list = [
            {
                key: value for key, value in entry['properties']['itemsKeyValue'].items()
            } for entry in self.content
        ]
        return pd.DataFrame(flat_list)


class WatchList:
    def watchlist(self, alias) -> list:
        uri = f'{self.base_uri}{self.workspace}/providers/Microsoft.SecurityInsights/watchlists/{alias}/watchlistItems'
        params = {'api-version': '2023-06-01-preview'}
        return Watchlist(content=self.get(uri, params=params)['value'])

    @property
    def watchlists(self) -> list:
        """Returns a list with all configured watchlists in
        workspace

        Returns:
            list: List containing available watchlists
        """
        uri = f'{self.base_uri}{self.workspace}/providers/Microsoft.SecurityInsights/watchlists'
        params = {'api-version': '2023-02-01'}
        results = self.get(uri, params=params)['value']
        all_watchlists = [{'name': ws['name'], 'createdAt': ws['systemData']['createdAt'],
                           'lastModifiedAt': ws['systemData']['lastModifiedAt']} for ws in results]
        return all_watchlists


class Sentinel(WatchList):
    def __init__(self, workspace: str = None):
        self.workspace = workspace


class Azure(Sentinel):
    """Generic Azure class containing methods to manage Sentinel
    content
    """
    def __init__(self, credential: 'DefaultAzureCredential' = None, subscription: str = None):
        self.base_uri = 'https://management.azure.com'
        self.credential = credential
        self.subscription = subscription

    def get(self, uri, params=None):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        results = requests.get(uri, params=params, headers=headers).json()
        return results

    @property
    def mgmt_endpoint(self) -> str:
        """Generates string containing the resource manager
        scope

        Returns:
            str: resource manager url scope
        """
        cloud = azure_cloud.AZURE_PUBLIC_CLOUD
        return f"{cloud.endpoints.resource_manager}.default"

    @property
    def token(self) -> str:
        """Generates access token based on mgmt_endpoint scope

        Returns:
            str: access token
        """
        token = self.credential.get_token(self.mgmt_endpoint)
        return token.token

    def resources(self, query: str) -> list:
        """Fetches resources from subscription

        Args:
            query (str): Query to filter resourxes

        Returns:
            list: List of resources
        """
        client = resourcegraph.ResourceGraphClient(self.credential)
        query_opts = resourcegraph.models.QueryRequestOptions(result_format="objectArray")
        query = resourcegraph.models.QueryRequest(subscriptions=[self.subscription], query=query, options=query_opts)
        results = client.resources(query)
        return results.data
