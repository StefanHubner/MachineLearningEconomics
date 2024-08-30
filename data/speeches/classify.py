import pandas as pd
from datetime import timedelta
import os

def load_speech_content(filename):
    try:
        with open(os.path.join('files', filename), 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {filename}: {str(e)}")
        return ""

def load_and_prepare_data(speeches_file, rates_file):
    # Load speeches with flexible date parsing
    speeches = pd.read_csv(speeches_file, sep=';', parse_dates=['Date'], 
                           date_parser=lambda x: pd.to_datetime(x, format='mixed', dayfirst=True))
    speeches = speeches.sort_values('Date')
    
    # Load speech content
    speeches['Speech'] = speeches['Filename'].apply(load_speech_content)

    # Load rates
    rates = pd.read_csv(rates_file, parse_dates=['Date Changed'], 
                        date_parser=lambda x: pd.to_datetime(x, format='%d %b %y'))
    rates = rates.sort_values('Date Changed')
    
    # Calculate rate changes
    rates['Previous Rate'] = rates['Rate'].shift(1)
    rates['Rate Change'] = (rates['Rate'] > rates['Previous Rate']).astype(int) * 2
    rates.loc[rates['Rate'] < rates['Previous Rate'], 'Rate Change'] = 0
    
    return speeches, rates

def classify_speeches(speeches, rates):
    classifications = pd.Series(1, index=speeches.index)  # Default classification is 1
    speech_rates = pd.Series(index=speeches.index)
    
    for i, speech in speeches.iterrows():
        # Find the most recent rate change before or on the speech date
        relevant_rate = rates[rates['Date Changed'] <= speech['Date']].iloc[-1]
        speech_rates[i] = relevant_rate['Rate']
        
        # Check if the speech is within 6 weeks before the next rate change
        next_change = rates[rates['Date Changed'] > speech['Date']]
        if not next_change.empty:
            next_change_date = next_change.iloc[0]['Date Changed']
            if (next_change_date - speech['Date']) <= timedelta(weeks=6):
                classifications[i] = next_change.iloc[0]['Rate Change']
    
    speeches['Rate'] = speech_rates
    speeches['Label'] = classifications
    
    return speeches[['Date', 'Speech', 'Rate', 'Label']]

def save_dataframe(df, output_file):
    df.to_csv(output_file, index=False, quoting=1, quotechar='"', escapechar='\\')


def load_classified_speeches(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, parse_dates=['Date'], quoting=1, quotechar='"', escapechar='\\')
    
    # Display basic information about the loaded data
    print(f"Loaded {len(df)} speeches")
    print("\nDataFrame Info:")
    print(df.info())
    
    print("\nFirst few rows:")
    print(df.head())
    
    return df


# You can now work with the speeches_df DataFrame
# For example, to get speeches with a specific label:
# upward_pressure_speeches = speeches_df[speeches_df['Label'] == 2]

# Or to get the average rate:
# average_rate = speeches_df['Rate'].mean()


def main():
    speeches_file = 'speeches.csv'
    rates_file = 'boe.csv'
    output_file = 'speeches_classified.csv'

    speeches, rates = load_and_prepare_data(speeches_file, rates_file)
    classified_speeches = classify_speeches(speeches, rates)
    save_dataframe(classified_speeches, output_file)

    print(f"Processing complete. Output written to {output_file}")
    
    speeches_df1 = load_classified_speeches(output_file)
    print("\nExample: Count of speeches by label")
    print(speeches_df1['Label'].value_counts())

if __name__ == "__main__":
    main()
