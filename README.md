# BugSystem_Analysis_Bugzilla_2023 (June/2023 - July/2023)
Database management with SQL and descriptive analysis with Python on bug records data
## Acknowledgement
This report has been adapted from the SMM695 final group project and refined to highlight my individual contributions. The link to the original project can be found below:
https://github.com/lyh1068/DBMS-SMM695
## Data Source
Bugzilla - a web-based general-purpose bug tracking system and testing tool originally developed and used by the Mozilla project
## Research Objectives & Approaches
This report seeks to explore data based on bug records from Bugzilla, the Mozilla project. The aim of the project is to execute a descriptive analysis on bug attributes to analyse the underlying relationships between these attributes.

- In the 1st phase the data was cleaned, manipulated and structured by Python. PostgreSQL was used to store and extract data. In particular, this part was conducted by my colleagues and is kept in this report to retain clarity; 

- In the 2nd phase, the data was queried and analysed. Descriptive analysis results were concluded, and business insights were summarised based on the data visualisations. User analysis and Timeseries analysis were conducted by Chuqiao Xiao, specifically; 

**SQL Database used**: PostgreSQL

**Special Python packages used**: Psycopg2

**BI tools**: Seaborn

## Research Results & Insights
- User Analysis:
  - Every bug has one developer in charge (solver), and almost every bug has one QA. Only a small group of users (3%) take the roles as solver and QA. About 70% of users were carbon copied with at least one bug record once.
  - It's identified that for the bugs that belongs to a certain product, the number of bugs is inversely proportional to the proportion of solvers working on that type of bugs. It indicates that the number of solvers assigned to a certain product type is relatively fixed. The more bugs are reported, the heavier workload one solver needs to take.
  - There are relatively more solvers working on bugs of “S2” and “N/A” within the Firefox severity system (Appendix 2), and more “blocker” and “trivial” in the default system. Considering that “S2” and “blocker” are the highest severity level, it can be implied that bugs with higher severity may have more developers working on them respectively, instead of being assigned to only a few same group of solvers. However, according to Figure 2 there are very few bugs of severity “S2”, “blocker”, therefore the alternative interpretation is that with the fewer number of these types of bugs, relatively more solvers would be able to work on them.
  - “P4” and “P5” are the priority levels that have more developers on average working on, but the ratios are overall low within a narrow range from 0.01 to 0.15. According to Figure 3, there are fewer bugs of priority “P4” and “P5”, which indicates that the lower number of bugs may result in the higher ratios. Nevertheless, the overall ratios of all priorities are close, implying that bugs with all priorities are equally assigned to a relatively same scale of solvers.
  - (To further prove the insights summarised above, ratios should be evened out on the basis of the number of bugs.)
- Timeseries Analysis:
  - The most frequently recorded intervals are “UNCONFIRMED_ RESOLVED”, “NEW_RESOLVED” and “RESOLVED_VERIFIED” which indicates that most bugs were resolved directly without going through the resolution process. By contrast, there are around 25 types of intervals that could not be found in the official document which are less frequently recorded. It cannot be inferred whether these bugs were recorded by mistake or they were just not recorded by the official document.
  - The average span between status changes has extreme values. According to the graph, “VERIFIED_RESOLVED”, “CLOSED_RESOLVED” and “ASSIGNED_UNCONFIRMED” are the extreme interval types. All anomaly types only have a few records and are not among the major resolving process according to the official document. The explanation to the extreme intervals is that only these few types of bugs exist in the system for a long time. These bugs can be hard to solved or harmless to the system so were left in the system.
  - The intervals that have extremely high variance are those types that have high mean values. The high variance indicates that the mean values of certain types of intervals may be influenced by a few extreme values among a smaller amount of data. The variance of “NEW_RESOLVED” is relatively higher than other common intervals, implying that this process might be diversified and less predictable compared to other common intervals.
  - The average time between the most regular statuses:
    ![image](https://github.com/XShawn1/BugSystem_Analysis_Bugzilla_2023/assets/113829962/ec8b370c-78d5-42b0-81b5-dd3102368799)


