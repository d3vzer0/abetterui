from azure.identity import DefaultAzureCredential
from libs.sentinel import Azure
import streamlit as st
import re
import os


@st.cache_resource
def cached_client():
    credential = DefaultAzureCredential()
    azure_client = Azure(credential, subscription=os.getenv('AZURE_SUB'))
    return azure_client


def workspace_sidebar(client):
    with st.sidebar:
        resource_filter = "Resources | where type =~ 'microsoft.operationsmanagement/solutions'| where name contains 'SecurityInsights'"
        workspaces = client.resources(resource_filter)
        workspace_selections = [
            {'id': ws['properties']['workspaceResourceId'], 'name': ws['name']} for ws in workspaces
        ]

        def format_workspace(input):
            ws_name = re.search('SecurityInsights\((.*)\)', input['name'])
            return ws_name.group(1)

        selected_workspace = st.selectbox('Select workspace', workspace_selections, format_func=format_workspace)
        client.workspace = selected_workspace['id']
        st.session_state["workspace"] = selected_workspace
