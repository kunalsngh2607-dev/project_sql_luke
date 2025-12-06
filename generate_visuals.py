
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker

# Ensure assets directory exists
if not os.path.exists('assets'):
    os.makedirs('assets')

# Set style
plt.style.use('ggplot')

# Load data
print("Loading data...")
try:
    df_jobs = pd.read_csv('csv_files/job_postings_fact.csv')
    df_skills = pd.read_csv('csv_files/skills_dim.csv')
    df_job_skills = pd.read_csv('csv_files/skills_job_dim.csv')
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    exit(1)

print("Data loaded. Processing...")

# --- 1. Top 5 In-Demand Skills ---
merged_df = df_jobs[df_jobs['job_title_short'] == 'Data Analyst'].merge(
    df_job_skills, on='job_id', how='inner'
).merge(
    df_skills, left_on='skill_id', right_on='skill_id', how='inner'
)

demand_counts = merged_df['skills'].value_counts().head(5)

plt.figure(figsize=(10, 6))
bars = plt.barh(demand_counts.index, demand_counts.values, color='skyblue')
plt.title('Top 5 In-Demand Skills for Data Analysts')
plt.xlabel('Number of Job Postings')
plt.ylabel('Skill')
plt.gca().invert_yaxis() # Highest on top
# Add values
for bar in bars:
    plt.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
             f'{int(bar.get_width())}', va='center')
plt.tight_layout()
plt.savefig('assets/in_demand_skills.png')
print("Saved in_demand_skills.png")


# --- 2. Top Paying Skills (Top 10) ---
df_salary = df_jobs[(df_jobs['job_title_short'] == 'Data Analyst') & (df_jobs['salary_year_avg'].notna())]
merged_salary = df_salary.merge(
    df_job_skills, on='job_id', how='inner'
).merge(
    df_skills, left_on='skill_id', right_on='skill_id', how='inner'
)

salary_stats = merged_salary.groupby('skills')['salary_year_avg'].agg(['mean', 'count']).reset_index()
top_paying_skills = salary_stats.sort_values(by='mean', ascending=False).head(10)

plt.figure(figsize=(10, 6))
bars = plt.barh(top_paying_skills['skills'], top_paying_skills['mean'], color='salmon')
plt.title('Top 10 High-Paying Skills for Data Analysts')
plt.xlabel('Average Yearly Salary')
plt.ylabel('Skill')
plt.gca().invert_yaxis()
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '${:,.0f}'.format(x)))
plt.tight_layout()
plt.savefig('assets/top_paying_skills.png')
print("Saved top_paying_skills.png")


# --- 3. Optimal Skills (Scatter Plot) ---
df_optimal = df_jobs[(df_jobs['job_title_short'] == 'Data Analyst') & 
                     (df_jobs['salary_year_avg'].notna()) &
                     (df_jobs['job_work_from_home'] == True)]

merged_optimal = df_optimal.merge(
    df_job_skills, on='job_id', how='inner'
).merge(
    df_skills, left_on='skill_id', right_on='skill_id', how='inner'
)

optimal_stats = merged_optimal.groupby('skills').agg(
    demand_count=('job_id', 'count'),
    avg_salary=('salary_year_avg', 'mean')
).reset_index()

optimal_stats = optimal_stats[optimal_stats['demand_count'] > 10]
optimal_top_25 = optimal_stats.sort_values(by=['avg_salary', 'demand_count'], ascending=[False, False]).head(25)

plt.figure(figsize=(10, 6))
plt.scatter(optimal_top_25['demand_count'], optimal_top_25['avg_salary'], 
            alpha=0.7, c='purple', s=optimal_top_25['demand_count']*2) # Size by demand

plt.title('Optimal Skills: Salary vs. Demand (Remote Data Analyst)')
plt.xlabel('Demand (Number of Job Postings)')
plt.ylabel('Average Yearly Salary')
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '${:,.0f}'.format(x)))

for i in range(len(optimal_top_25)):
    row = optimal_top_25.iloc[i]
    plt.text(row['demand_count'], row['avg_salary'], row['skills'], fontsize=9)

plt.tight_layout()
plt.savefig('assets/optimal_skills.png')
print("Saved optimal_skills.png")

print("All visuals generated.")
