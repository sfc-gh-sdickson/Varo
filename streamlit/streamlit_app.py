import streamlit as st
   import snowflake.connector
   import pandas as pd
   import json
   import random
   from datetime import datetime

   # Connect to Snowflake
   conn = st.connection("snowflake")
   cur = conn.cursor()

   st.title("Varo Bank Intelligence Demo (with Anomaly Detection)")

   # User Input
   user_query = st.text_input("Ask about customers, accounts, transactions, loans, credit cards, fraud, anomalies, or feedback (e.g., 'Detect anomalies in transactions' or 'Predict fraud on a transaction')")

   if user_query:
       if 'search' in user_query.lower() or 'feedback' in user_query.lower():
           # Cortex Search for unstructured feedback
           search_query = user_query.replace('search', '').strip()
           result = cur.execute(f"""
               SELECT CORTEX_SEARCH(BANKING.VARO_FEEDBACK_SEARCH, 
                   '{{"query": "{search_query}", "columns": ["FEEDBACK_TEXT", "SENTIMENT"], "filter": {{}}}}')
           """).fetchall()
           df = pd.DataFrame(result, columns=['FEEDBACK_TEXT', 'SENTIMENT', 'SCORE'])
           st.write("Feedback Search Results:")
           st.dataframe(df)
       elif 'predict fraud' in user_query.lower():
           # ML Fraud Prediction using Snowflake ML Model
           # Generate sample transaction data for demo
           sample_amount = random.uniform(10, 1000)
           sample_type = random.choice(['Deposit', 'Withdrawal', 'Transfer'])
           sample_category = random.choice(['Groceries', 'Utilities', 'Salary', 'Entertainment', 'Travel'])
           sample_date = datetime.now().isoformat()
           
           predict_sql = f"""
               SELECT BANKING.FRAUD_MODEL!PREDICT(INPUT_DATA => OBJECT_CONSTRUCT(
                   'AMOUNT', {sample_amount},
                   'TRANSACTION_TYPE', '{sample_type}',
                   'CATEGORY', '{sample_category}',
                   'TRANSACTION_DATE', '{sample_date}'
               )) AS prediction;
           """
           result = cur.execute(predict_sql).fetchone()[0]
           prediction_json = json.loads(result)
           fraud_class = prediction_json['class']
           fraud_prob = prediction_json['probability'][str(fraud_class)]
           
           st.write(f"Sample Transaction: Amount={sample_amount:.2f}, Type={sample_type}, Category={sample_category}, Date={sample_date}")
           st.write(f"Predicted Fraud: {'Yes' if fraud_class else 'No'} (Probability: {fraud_prob:.2f})")
       elif 'anomal' in user_query.lower():  # Detect anomalies
           # Anomaly Detection using Snowflake ML Model
           # Query recent daily data and detect anomalies
           anomaly_sql = """
               CALL BANKING.TRANSACTION_ANOMALY_MODEL!DETECT_ANOMALIES(
                   INPUT_DATA => SYSTEM$QUERY_REFERENCE('SELECT TS, TOTAL_AMOUNT FROM BANKING.DAILY_TRANSACTIONS ORDER BY TS DESC LIMIT 90'),
                   TIMESTAMP_COLNAME => 'TS',
                   TARGET_COLNAME => 'TOTAL_AMOUNT'
               );
           """
           df = conn.query(anomaly_sql)
           st.write("Anomaly Detection Results (Last 90 Days):")
           st.dataframe(df)
           
           # Chart with anomalies highlighted
           df['IS_ANOMALY'] = df['IS_ANOMALY'].astype(bool)
           fig = st.line_chart(df, x='TS', y='TOTAL_AMOUNT')
           anomalies = df[df['IS_ANOMALY']]
           if not anomalies.empty:
               st.write("Anomalous Points:")
               st.dataframe(anomalies[['TS', 'TOTAL_AMOUNT', 'LOWER_BOUND', 'UPPER_BOUND']])
               st.line_chart(anomalies, x='TS', y='TOTAL_AMOUNT', color='red')
       else:
           # Cortex Analyst for structured data via Semantic View
           result = cur.execute(f"""
               SELECT snowflake.cortex.analyst_process_message(
                   (SELECT VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS 
                    WHERE TABLE_SCHEMA = 'BANKING' AND TABLE_NAME = 'VARO_SEMANTIC_VIEW'), 
                   '{user_query}'
               )
           """).fetchone()[0]
           
           response_json = json.loads(result)
           sql = response_json.get('sql')
           if sql:
               df = conn.query(sql)
               st.write("Query Results:")
               st.dataframe(df)
               
               # Generate Chart if requested
               if 'chart' in user_query.lower() or 'trend' in user_query.lower() or 'distribution' in user_query.lower():
                   if 'transaction' in user_query.lower() and 'TRANSACTION_DATE' in df.columns and 'AMOUNT' in df.columns:
                       st.line_chart(df, x='TRANSACTION_DATE', y='AMOUNT')
                   elif 'balance' in user_query.lower() and 'ACCOUNT_TYPE' in df.columns and 'BALANCE' in df.columns:
                       st.bar_chart(df, x='ACCOUNT_TYPE', y='BALANCE')
                   elif 'loan' in user_query.lower() and 'LOAN_TYPE' in df.columns:
                       st.pie_chart(df, x='LOAN_TYPE', y='COUNT')
                   elif 'credit' in user_query.lower() and 'ISSUE_DATE' in df.columns and 'CURRENT_BALANCE' in df.columns:
                       st.area_chart(df, x='ISSUE_DATE', y='CURRENT_BALANCE')
                   elif 'fraud' in user_query.lower() and 'FRAUD_TYPE' in df.columns:
                       st.bar_chart(df, x='FRAUD_TYPE', y='COUNT')
                   st.write("Generated Chart based on query.")

   # Close connection
   conn.close()
