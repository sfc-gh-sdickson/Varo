# Snowflake Intelligence Demo Setup for Varo Bank (Enhanced with Anomaly Detection)

   This guide provides step-by-step instructions to set up the enhanced Snowflake Intelligence demo for Varo Bank, incorporating detailed banking elements (customers, accounts, transactions, feedback, loans, credit cards, fraud detection), ML fraud prediction, and now anomaly detection using Snowflake ML ANOMALY_DETECTION for time-series anomalies (e.g., unusual daily transaction volumes). It uses Snowflake Cortex AI features and Streamlit for interactive visualizations and predictions. Assumes a Snowflake account with Cortex AI and Snowflake ML enabled.

   ## Prerequisites
   - Snowflake account with Cortex AI (Analyst and Search) and Snowflake ML (Classification, Anomaly Detection) enabled.
   - Snowsight for Streamlit, SQL execution, and ML model management.
   - A warehouse (e.g., COMPUTE_WH) for queries and ML training (recommend Medium Snowpark-optimized for ML).
   - Basic SQL and Python knowledge.

   ## Step 1: Create Database, Schema, and Tables
   Run `sql/create_database.sql` to create the database, schema, and tables, including `IS_FRAUD` in `TRANSACTIONS` for ML training labels and `FRAUD_DETECTION` for fraud analysis.

   ## Step 2: Load Synthetic Data
   Run `sql/load_data.sql` to generate scaled synthetic data (~1000 customers, ~2000 accounts, ~100,000 transactions with ~1% fraud labels, ~5000 feedback entries, ~1500 loans, ~1500 credit cards, ~10,000 fraud detection records).

   ## Step 3: Create ML Fraud Prediction Model
   Run `sql/create_ml_model.sql` to train a classification model (`FRAUD_MODEL`) on transaction features to predict fraud.

   ## Step 4: Create Anomaly Detection Model
   Run `sql/create_anomaly_model.sql` to create a time-series view (`DAILY_TRANSACTIONS`) and train the anomaly detection model (`TRANSACTION_ANOMALY_MODEL`) for detecting unusual daily transaction volumes.

   ## Step 5: Create Semantic View for Cortex Analyst
   Run `sql/create_semantic_view.sql` to create a Semantic View for natural language queries on structured data, including fraud and anomaly-related fields.

   ## Step 6: Set Up Cortex Search for Unstructured Data
   Run `sql/create_cortex_search.sql` to create a Cortex Search service for hybrid search on customer feedback.

   ## Step 7: Deploy Streamlit App for Queries, Charts, ML Predictions, and Anomaly Detection
   The Streamlit app supports queries, charts, fraud predictions, and anomaly detection.

   1. Create stage: `CREATE STAGE IF NOT EXISTS BANKING.VARO_STAGE;`
   2. Upload `streamlit/app.py`: `PUT file:///path/to/app.py @BANKING.VARO_STAGE/streamlit/;`
   3. Create Streamlit:
      ```sql
      CREATE STREAMLIT BANKING.VARO_INTELLIGENCE_APP
          ROOT_LOCATION = '@BANKING.VARO_STAGE/streamlit/'
          MAIN_FILE = '/app.py'
          QUERY_WAREHOUSE = <your_warehouse>;
      ```
   4. Grant access: `GRANT USAGE ON STREAMLIT BANKING.VARO_INTELLIGENCE_APP TO ROLE PUBLIC;`
   5. Run in Snowsight under "Apps" > "Streamlit".

   ## Step 8: Test the Demo
   - **Structured Queries**: "Average amount for fraudulent transactions" or "Fraud count by category." Shows results and charts.
   - **Unstructured Queries**: "Search for negative fraud feedback."
   - **ML Fraud Prediction**: Try "Predict fraud on a transaction." Generates a sample transaction and predicts fraud probability.
   - **Anomaly Detection**: Try "Detect anomalies in transactions." Runs the model on the last 90 days' daily totals, showing results and charts with anomalies in red.
   - **Business Insights**: Enables ML-driven fraud prediction, anomaly detection for proactive monitoring, and comprehensive banking analysis.

   ## Troubleshooting
   - Ensure Snowflake ML (Classification and ANOMALY_DETECTION) and Cortex AI are enabled (see docs.snowflake.com).
   - For ML training errors, check warehouse size (Medium+ recommended) and data volume.
   - Grant necessary privileges:
     ```sql
     GRANT CREATE SNOWFLAKE.ML.CLASSIFICATION ON SCHEMA BANKING TO ROLE <your_role>;
     GRANT CREATE SNOWFLAKE.ML.ANOMALY_DETECTION ON SCHEMA BANKING TO ROLE <your_role>;
     ```
   - Monitor warehouse usage for large data loads (~100,000 transactions, ~10,000 fraud records).

   Upload files to https://github.com/sfc-gh-sdickson/Varo. For further enhancements (e.g., per-customer anomalies), contact the repository owner.