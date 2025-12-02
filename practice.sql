SELECT 
    count(job_id),
    extract(month from job_posted_date) as date_month
FROM 
    job_postings_fact
WHERE 
    job_title_short = 'Data Analyst'
group by 
    date_month;