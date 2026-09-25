"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`

    Approach:
    - The customers table contains duplicated CustomerIDs. These are removed
      so that duplicated customers are not counted twice and do not skew the
      average income.
    - The deduplicated cutomers are joined to the credit table to obtain 
      each customer's CustomerClass.
    """
    
    qry = """
            -- Get unique list of customers and their income
            WITH unique_customers AS (
                SELECT DISTINCT CustomerId, Income 
                FROM customers
            )

            -- Join to credit data and average income per class
            SELECT 
                ct.CustomerClass, 
                AVG(uc.Income) AS AverageIncome  
            FROM unique_customers uc
            INNER JOIN credit ct 
                ON uc.CustomerId = ct.CustomerId
            GROUP BY ct.CustomerClass
            ORDER BY ct.CustomerClass
        """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.

    Approach:
    - Map full names to abbreviated Provice names as found in the customers table. 
    - Both the customers and loan tables contain duplicate CustomerIDs. Exact duplicate 
      loans are removed so that rejected applications are not counted more than once.
    - Province values are standerdised before deduplication so that a customer recorded
      as the abbreviated and full name collapses into a single row. 
    """
    
    qry = """
            -- Standardise provice names and deduplicate customers
            WITH unique_customers AS (
                SELECT DISTINCT 
                    CustomerId, 
                    CASE TRIM(Region)
                        WHEN 'EasternCape'   THEN 'EC'
                        WHEN 'FreeState'     THEN 'FS'
                        WHEN 'Gauteng'       THEN 'GT'
                        WHEN 'KwaZulu-Natal' THEN 'KZN'
                        WHEN 'Limpopo'       THEN 'LP'
                        WHEN 'Mpumalanga'    THEN 'MP'
                        WHEN 'NorthernCape'  THEN 'NC'
                        WHEN 'NorthWest'     THEN 'NW'
                        WHEN 'WesternCape'   THEN 'WC'
                        ELSE TRIM(Region)
                    END AS Province
                FROM customers
            ),
            
            -- Remove exact duplicate loan records
            unique_loans AS (
                SELECT DISTINCT * FROM loans
            )

            -- Count rejected applications per province
            SELECT 
                uc.Province, 
                COUNT(*) AS RejectedApplications
            FROM unique_customers uc
            INNER JOIN unique_loans ul 
                ON uc.CustomerId = ul.CustomerId
            WHERE ul.ApprovalStatus = 'Rejected'
            GROUP BY uc.Province
            ORDER BY uc.Province
        """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.

    Approach:
    - The table structure is defined first with CREATE OR REPLACE, so that
      the query can be executed safely more than once.
    - Each source table is deduplicated first as it would otherwise multiply 
      rows in the join
    - Loans is the base table and LEFT JOIN is used so every loan is kept even 
      if a matching customer or credit record is missing.
    """
    
    qry = """
            -- Define the table structure 
            CREATE OR REPLACE TABLE financing (
                CustomerID     INTEGER,
                Income         INTEGER,
                LoanAmount     INTEGER,
                LoanTerm       INTEGER,
                InterestRate   FLOAT,
                ApprovalStatus VARCHAR,
                CreditScore    INTEGER
            );

            -- Populate the table from deduplicated source data
            INSERT INTO financing
            WITH unique_customers AS (
                SELECT DISTINCT 
                    CustomerID,
                    Income
                FROM customers
            ),
            unique_loans AS (
                SELECT DISTINCT * FROM loans 
            ),
            unique_credit AS (
                SELECT DISTINCT 
                    CustomerID,
                    CreditScore
                FROM credit
            )
            SELECT 
                ul.CustomerID,
                uc.Income,
                ul.LoanAmount,
                ul.LoanTerm,
                ul.InterestRate,
                ul.ApprovalStatus,
                ucr.CreditScore
            FROM unique_loans ul
            LEFT JOIN unique_customers uc 
                ON ul.CustomerID = uc.CustomerID
            LEFT JOIN unique_credit ucr 
                ON ul.CustomerID = ucr.CustomerID
        """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.

    Approach:
    - The table structure is defined first with CREATE OR REPLACE, so that
      the query can be executed safely more than once.
    - Each RepaymentDate is recorded in the customer's local time.
    - Abbreviations are mapped to IANA region names.
    - Each timestamp is then converted to London time
    - Only repayments made between 06:00 and 18:00 London time are kept
      and are aggregated per customer per month
    - A CROSS JOIN of all customers with the months table creates all 12
      months for every customer. 
    - The monthly aggreagates are LEFT JOINED onto this and months without
      repayments are  filled with 0.
    """

    qry = """CREATE OR REPLACE TABLE timeline (
                CustomerID          INTEGER,
                MonthName           VARCHAR,
                NumberOfRepayments  INTEGER,
                AmountTotal         INTEGER
            );

            INSERT INTO timeline

            -- Map different timezone abbreviations into IANA region names
            WITH payments_rezoned AS ( 
                SELECT
                    CustomerID,
                    Amount,
                    RepaymentDate,
                    CASE UPPER(TRIM(TimeZone))
                        WHEN 'JST' THEN 'Asia/Tokyo'
                        WHEN 'PST' THEN 'America/Los_Angeles'
                        WHEN 'CET' THEN 'Europe/Paris'
                        WHEN 'PNT' THEN 'America/Phoenix'
                        WHEN 'UTC' THEN 'UTC'
                        WHEN 'EET' THEN 'Europe/Athens'
                        WHEN 'GMT' THEN 'UTC'
                        WHEN 'IST' THEN 'Asia/Kolkata'
                        WHEN 'CST' THEN 'America/Chicago'
                        END AS IanaZone
                FROM repayments
            ),

            -- Convert local timezones to London times
            payment_london_timezoned AS (
                SELECT
                    CustomerID,
                    Amount,
                    timezone('Europe/London', timezone(IanaZone, RepaymentDate)) AS LondonTime
                FROM payments_rezoned
            ),

            -- Keep repayments between 06:00 and 18:00 London time
            -- Aggregate per customer per month
            monthly_repayments AS (
                SELECT
                    CustomerID,
                    MONTH(LondonTime) AS MonthID,
                    COUNT(*) AS NumberOfRepayments,
                    SUM(Amount) AS AmountTotal
                FROM payment_london_timezoned
                WHERE CAST(LondonTime AS TIME) BETWEEN TIME '06:00:00' AND TIME '18:00:00'
                GROUP BY CustomerID, MONTH(LondonTime)
            ),

            -- Get unique customers
            unique_customers AS (
                SELECT DISTINCT CustomerID FROM customers
            )

            -- Every customer x every month filling gaps with 0
            SELECT
                c.CustomerID,
                m.MonthName,
                COALESCE(r.NumberOfRepayments, 0) AS NumberOfRepayments,
                COALESCE(r.AmountTotal, 0)        AS AmountTotal
            FROM unique_customers c
            CROSS JOIN months m
            LEFT JOIN monthly_repayments r
                ON  r.CustomerID = c.CustomerID
                AND r.MonthID    = m.MonthID
            ORDER BY c.CustomerID, m.MonthID"""

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1

    APPROACH:
    - The timeline table holds one row per customer per month. Grouping by
      CustomerId collapses the 12 monthly rows into 1 row.
    - For each month the CASE expression selects that month's value and the
      SUM returns that month's value. 
    """

    qry = """
            SELECT
                CustomerID,
    
                CAST(SUM(CASE WHEN MonthName = 'January'   THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JanuaryRepayments,
                SUM(CASE WHEN MonthName = 'January'   THEN AmountTotal ELSE 0 END)                         AS JanuaryTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'February'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS FebruaryRepayments,
                SUM(CASE WHEN MonthName = 'February'  THEN AmountTotal ELSE 0 END)                         AS FebruaryTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'March'     THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MarchRepayments,
                SUM(CASE WHEN MonthName = 'March'     THEN AmountTotal ELSE 0 END)                         AS MarchTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'April'     THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AprilRepayments,
                SUM(CASE WHEN MonthName = 'April'     THEN AmountTotal ELSE 0 END)                         AS AprilTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'May'       THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MayRepayments,
                SUM(CASE WHEN MonthName = 'May'       THEN AmountTotal ELSE 0 END)                         AS MayTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'June'      THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JuneRepayments,
                SUM(CASE WHEN MonthName = 'June'      THEN AmountTotal ELSE 0 END)                         AS JuneTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'July'      THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JulyRepayments,
                SUM(CASE WHEN MonthName = 'July'      THEN AmountTotal ELSE 0 END)                         AS JulyTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'August'    THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AugustRepayments,
                SUM(CASE WHEN MonthName = 'August'    THEN AmountTotal ELSE 0 END)                         AS AugustTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS SeptemberRepayments,
                SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END)                         AS SeptemberTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'October'   THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS OctoberRepayments,
                SUM(CASE WHEN MonthName = 'October'   THEN AmountTotal ELSE 0 END)                         AS OctoberTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'November'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS NovemberRepayments,
                SUM(CASE WHEN MonthName = 'November'  THEN AmountTotal ELSE 0 END)                         AS NovemberTotal,
    
                CAST(SUM(CASE WHEN MonthName = 'December'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS DecemberRepayments,
                SUM(CASE WHEN MonthName = 'December'  THEN AmountTotal ELSE 0 END)                         AS DecemberTotal
        
            FROM timeline
            GROUP BY CustomerID
            ORDER BY CustomerID
        """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)

    Approach:
    - Misalignment occured separately in the original male and female tables
      so every window is partitioned by Gender.
    - Ages shifted two places upwards so each customer's true age is found 
      two rows above.
    - The first two customers of each gender have no row two above. Their
      true ages are overflowed from the last two rows of that gender. 
    - Duplicated Ids are removed first as the extra rows would offset the
      row positions.
    """

    qry = """
            CREATE OR REPLACE TABLE corrected_customers AS

            -- Remove duplicate customer records
            WITH unique_customers AS (
                SELECT DISTINCT CustomerID, Age, Gender
                FROM customers
            ),

            -- Get the row number of each customer within their gender
            -- Get the number of customers in that gender group
            customer_positions AS (
                SELECT 
                    CustomerID,
                    Age,
                    Gender,
                    ROW_NUMBER() OVER (PARTITION BY Gender ORDER BY CustomerID) AS rn,
                    COUNT(*) OVER (PARTITION BY Gender) AS cnt
                FROM unique_customers
            ),

            -- Get the age two rows above
            -- Get the ages in the last two rows of the gender
            customers_shifted AS (
                SELECT 
                    CustomerID,
                    Age,
                    Gender,
                    rn,
                    LAG(Age, 2) OVER (PARTITION BY Gender ORDER BY CustomerID) AS LaggedAge,
                    MAX(CASE WHEN rn = cnt - 1 THEN Age END) OVER (PARTITION BY Gender) AS SecondLastAge,
                    MAX(CASE WHEN rn = cnt THEN Age END) OVER (PARTITION BY Gender) AS LastAge
                FROM customer_positions
            )

            -- Select the correct age for each row
            SELECT 
                CustomerID,
                Age,
                CASE rn
                    WHEN 1 THEN SecondLastAge
                    WHEN 2 THEN LastAge
                    ELSE LaggedAge
                END AS CorrectedAge,
                Gender
            FROM customers_shifted
            ORDER BY CustomerID;

            -- Return the result set
            SELECT * FROM corrected_customers ORDER BY CustomerID
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`

    Approach:
    - The AgeCategory column is added with IF NOT EXISTS which allows the query to be 
      executed more than once safely.
    - Repayments are counted per customer by counting DISTINCT RepaymentIDs. 
    - LEFT JOIN is used so customers with no repayments are kep and given a 
      count of 0.
    - Customers are ranked within their age group by total repyaments
      using DENSE_RANK which does not skip numbers after ties. 
    """

    qry = """
        -- Add and popualte the AgeCategory column
        ALTER TABLE corrected_customers ADD COLUMN IF NOT EXISTS AgeCategory VARCHAR;
        
        UPDATE corrected_customers
        SET AgeCategory = CASE
            WHEN CorrectedAge < 20 THEN 'Teen'
            WHEN CorrectedAge < 30 THEN 'Young Adult'
            WHEN CorrectedAge < 60 THEN 'Adult'
            ELSE 'Pensioner'
        END;

        -- Get the total number of repayments per customer
        WITH customer_repayments AS (
            SELECT
                CustomerID,
                COUNT(DISTINCT RepaymentID) AS TotalPaymentsPerCustomer
            FROM repayments
            GROUP BY CustomerID
        )

        -- Rank customers within their age group by total repayments.
        SELECT 
            cc.CustomerID,
            cc.Age,
            cc.CorrectedAge,
            cc.Gender,
            cc.AgeCategory,
            DENSE_RANK() OVER (
                PARTITION BY cc.AgeCategory
                ORDER BY COALESCE(cr.TotalPaymentsPerCustomer, 0) DESC
            ) AS "Rank"
        FROM corrected_customers cc
        LEFT JOIN customer_repayments cr
            ON cc.CustomerID = cr.CustomerID
        ORDER BY cc.AgeCategory, "Rank", cc.CustomerID;
    """

    return qry
