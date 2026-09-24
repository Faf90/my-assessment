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
Each question in this section is isolated, for example, you do not need to consider how Q5 may affect Q4.
Remember to clean your data.

"""


def question_1():
    """
    Find the name, surname and customer ids for all the duplicated customer ids in the customers dataset.
    Return the `Name`, `Surname` and `CustomerID`

    Approach: 
    - A subquery identifies CustomerIDs that occur more than once. 
    - The outer query returns the name details for those CustomerIDs.
    """

    qry = """
            SELECT DISTINCT
                c.Name, 
                c.Surname, 
                c.CustomerId 
            FROM customers c 
            WHERE CustomerId IN (
                SELECT CustomerId
                From customers
                GROUP BY CustomerID
                HAVING COUNT(*) > 1
            )
            ORDER BY CustomerId"""

    return qry


def question_2():
    """
    Return the `Name`, `Surname` and `Income` of all female customers in the dataset in descending order of income

    Approach: 
    - The customers table is deduplicated first to ensure
      each customer appears only once. 
    - Results are ordered by income, highest first.
    """

    qry = """
            WITH unique_customers AS (
                SELECT DISTINCT
                    Name, 
                    Surname, 
                    Income,
                    Gender
                FROM customers
            )
            SELECT 
                c.Name, 
                c.Surname, 
                c.Income 
            FROM customers c 
            WHERE c.Gender = 'Female' 
            ORDER BY c.Income DESC
        """

    return qry


def question_3():
    """
    Calculate the percentage of approved loans by LoanTerm, with the result displayed as a percentage out of 100.
    ie 50 not 0.5
    There is only 1 loan per customer ID.

    Approach:
    - Duplicate CustomerIds exists with exact row values. 
      filter out duplicates before calculating the percentage of 
      approved loans by LoanTerm.
    """
    
    qry = """
            WITH deduplicated AS (
                SELECT DISTINCT * FROM loans
            )
            SELECT 
                LoanTerm, 
                100.0 * SUM(CASE WHEN ApprovalStatus = 'Approved' THEN 1 ELSE 0 END) / COUNT(*) AS ApprovedPercentage
            FROM deduplicated
            GROUP BY LoanTerm
            ORDER BY LoanTerm
        """

    return qry


def question_4():
    """
    Return a breakdown of the number of customers per CustomerClass in the credit data
    Return columns `CustomerClass` and `Count`

    Approach:
    - Count distinct CustomerIds so that a customer apearing more than once are counted only once.
    """

    qry = """
            SELECT 
                CustomerClass, 
                COUNT(DISTINCT CustomerId) AS Count 
            FROM credit
            GROUP BY CustomerClass
            ORDER BY CustomerClass
        """

    return qry


def question_5():
    """
    Make use of the UPDATE function to amend/fix the following: Customers with a CreditScore between and including 600 to 650 must be classified as CustomerClass C.

    Approach:
    - UPDATE CustomerClass to C for scores between and including 600 to 650.
    - Only rows in that range are affected.
    """
    
    qry = """
            UPDATE credit
            SET CustomerClass = 'C'
            WHERE CreditScore BETWEEN 600 AND 650
        """

    return qry
