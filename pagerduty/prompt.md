You have messed things up. Please create a brand new project code base, and mark all the files surfaced as _v2. 
1) Have a centralized Incident Object class as data transfer object between the PagerDuty APIs and Database update/retrival object. This object should have key incident information like ID, name, status, and a label indicates whether the incident has ever been escalated. This class should not have any functions talking to database or pagerduty APIs.
2) Have a centralized PagerDuty API client, that feteches incidents from the services interested (honors the PagerDuty.yaml) for the previous X days (GTC-7 timezone). For each incident make sure to have another call to get log_entries, and from the log_entries if we have activities typed as "escalate_log_entry", mark the incident as escalated. This client should marshall the API response into the Incident Object. 
3) Have a centralized database access layer. Store and fetch Incident Objects through the database. 
4) Have a centralized data analysis layer that create metrics as needed. This layer issues SQL queries into the database and calcuate metrics like "total triggered incident in the last X days", "total excalated incidents in the last X days", etc...
5) Create a Main file code that can tigger some commands: update incident for the last X days (fetching data from PagerDuty and update database); show summary status for the metrics interested. 


Now create a new UI, mark all the code surfaced as _v2
1) A dashboard page with multiple tabs, one service per tab. In each tab shows a calendar view and on each day of the calendar display the incident count, escalated count, etc. Also showing a summary of the metrics in past 7 days or 30 days, along with a chart showing the trends for either last 7 days or 30 days based on user selection. 
2) A simple Admin page that allows me to trigger the "--update-summary" command to refresh the data for the last X day. Selectable but maximum to 7 days. 


Awesome Job! I need you to do a few more UI enhancements: 
1) For the "escalated" badages on each day of the calendar, add a hover popup function. In the popup shows the hyperlink for the escalated incidents that can direct me to the PagerDuty incident page. 
2) The UI element looks pretty big, make them smaller and nicer.


Add a new feature of adding two more metrics: Incidents that resolved by CCOE; Incident caused by Infrastructure issue. 
1) For each incident call another API <incident_id>/custom_fields/values to get more attributes. If the "resolution" field is "ccoe", it indicates the incident is being solved by CCOE; If the "prelim_root_cause" field has falues of "rheos", "hadoop", "tess", etc. it indicates the incident is casued by infrastructure issue. Make sure you include this API call in the batch along with the "log_entries" as well to speed up the processing. 
2) Extend the Incident object, the corresponding database, etc... to include the two new attributes. 
3) Add new metrics that calculate "Incidents that resolved by CCOE" and "Incident caused by Infrastructure issue".
4) Change UI (calendar entry, metric labels, chart) to include these two new metrics