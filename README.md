# Cisco U. Spotlight 2025 - "Splunk"ing Your Way to Self-Healing Networks"

## Overview

Thsis repository contains the code and resources for the Cisco U. Spotlight 2025 session on "Splunk"ing Your Way to Self-Healing Networks". The session focuses on how to leverage Splunk's capabilities to create self-healing networks, enhancing network reliability and performance, using outbound webhooks from Splunk to a webhook receiver which parses the received information and use it to drive automations based on SSH and API-based information.  **This is not production code** and it is intended for educational purposes only. The code is provided as-is and should be used at your own risk. Please ensure you have the necessary permissions and understanding before running any scripts or automations in a production environment.

## Assets

There are several folders included within this repository to aid in your self-healing network journey.

- [`meraki`](https://github.com/qsnyder/spotlight-2025/tree/main/meraki) -- this includes the webhook listener and Python requirements needed to create the webhook receiver that will listen to events from Splunk, pass them to a Webex messaging webhook room, and then use the resulting information to drive automation by looking at a change and comparing it to what exists within Netbox, which is used as a single source of truth for IP information.
- [`syslog`](https://github.com/qsnyder/spotlight-2025/tree/main/syslog) -- this includes the webhook listener and Python requirements needed to create the webhook receiver that will listen to the resulting webhooks generated from syslog messages into Splunk.  This listener will forward information to a Webex messaging webhook room, and then use the resulting information to drive automation based on a regular expression query of the syslog data.  The change will be performed using SSH and Netmiko against the device that generated the syslog message.
- [`webhook-examples`](https://github.com/qsnyder/spotlight-2025/tree/main/webhook-examples) -- this includes examples of the webhook payloads that were generated as part of this session.  It includes webhooks from Meraki for both an API-related as well as a dashboard-initiated change, as well as a syslog webhook that was initiated from Splunk.  These examples are provided to help you understand the structure of the webhooks and how to parse them for your own use cases.
- [`assets`](https://github.com/qsnyder/spotlight-2025/tree/main/assets) -- this folder includes the sample topology used within CML for the syslog-based segment of the session.

## Scaffolding the Splunk Instance

You'll need to create several different components to segregate the data within the platform.  Some of these are optional (and will be noted as such), while others are required in order to ingest the data.

### Indexes for Data

#### Defining What Requires an Index

Different sets of data can be placed into different indexes, depending on the requirements and needs of your organization.  While the scope of "why" you would do this is beyond the scope of this session, there are a few general best practices:

- **Does the data need to be segmented via Role-Based Access Control (RBAC)?**
  - If the data needs to be segmented from the view of different users, it will need to be placed in a unique index
- **Do unique data retention requirements exist between types of data?**
  - Data retention is defined *per index*, so if there are different requirements, different indexes will be required
- **Do the different data sources have different data volumes?**
  - While not a massive issue, if you have data sources that generate 1000s of events per hour, while another source that generates a few events per day -- you may want to segment the data purely from a refinement and visibility standpoint

Splunk **does not** require different data types/structures to be segmented into different indexes, so that does not need to be a defining factor.

#### Creating the Index

If it is determined that you need a unique index (or want to place the data outside of the default main index), here are the steps required:

1. Click on **Settings > Indexes**

![index creation step 1](images/index-1.png)

2. Give the new index a name.  You can change the other settings, including size and retention if desired.  Click **Save** when completed

![index creation step 2](images/index-2.png)

3. The index will now be available for data source ingestion

### Creating a Local Listener (e.g. syslog)

In order to accept data being sent from sources, you need to define data input within the Splunk platform.  This creates the "listener" within Splunk to accept the data being sent to it.

#### Defining a Syslog Listener

To create a syslog listener for splunk (the first part of the demo), perform the following actions:

1. Click on **Settings > Data Inputs > UDP**.  This is due to syslog being sent along a UDP port

![syslog-listener step 1](images/udp-inputs.png)

2. Click on **New Local UDP**

3. Define the transport type and port number, as well as any overrides necessary.  For syslog, use `udp/514`.  Click **Next**

![syslog-listener step 2](images/syslog-1.png)

4. Select the data source type.  In this case, we'll be sending syslog data from Cisco devices, so search for `cisco_syslog` and select that option.  Click **Next** when done

![syslog-listener step 3](images/syslog-2.png)

5. Select the index in which you'd like to place the data.  In this case, we're placing it in a net-new index created for the syslog data.  Click **Next** when complete

![syslog-listener step 4](images/syslog-3.png)

6. Finally, review the settings to make sure that everything is correct.  Click **Submit** when completed

![syslog-listener step 5](images/syslog-4.png)

### Creating a Web Listener (Webhook Events)

## Creating Webex Webhook Listeners

## Using the Splunk Webhook Middleware

## A Note About Webhooks from Splunk

If you test your outbound Splunk webhooks using something like [webhook.site](https://www.webhook.site), you'll notice that the resulting output differs from the input, especially where JSON webhooks are concerned.

Generally, webhooks will be in JSON format and can be nested (e.g. lists and dictionaries can exist within top-level keys).  This can be seen in the example webhook from Meraki found [here](webhook-examples/meraki-api-webhook.json).  Notice, specifically that there exists some data under the **[event][alertData][changes][apiChanges]** path.

If we were to compare that to what is seen in Splunk (and therefore seen outbound in a webhook from Splunk), you'll see the following

![flattened splunk outputs](images/flattened-splunk.png)

Note that the paths that existed as part of nested key/value pairs are now given as "flat" dotted-notation (similar to what is seen in something like a Python method call or so).  What is seen in the image above, is sent in the webhook.  This can cause issues, as you're no longer able to build conditionals based on the "nested" nature of the payload directly from the webhook.

This is why the session focuses on using the `[_raw]` key within the data from Splunk in the listener itself.  It is possible to conver this key into searchable JSON and then query as you would directly from the source data itself.