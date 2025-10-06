## Question 3: Performance Analysis (CRUD Operations)

Tested how quickly each design performs standard database operations: Create, Read, Update, and Delete across both MongoDB collections.

### Observations:

• **Create Operations:**
  - Bulk Insert: Customer-centric design is significantly faster (0.005815s vs 0.011436s) due to fewer documents being created.
  - Single Insert: Both designs perform similarly, with transaction-centric slightly faster (0.000514s vs 0.000628s) due to smaller document size.

• **Read Operations:**
  - Customer Data Lookup: Customer-centric design is 56% faster (0.000440s vs 0.000688s) since all customer data is in one document.
  - Sales by Country: Transaction-centric design is 48% faster (0.000398s vs 0.000771s) as aggregation is more direct.
  - Invoice Lookup: Transaction-centric design is 27% faster (0.000405s vs 0.000556s) since invoices are top-level documents.
  - Transaction Count: Transaction-centric design is 52% faster (0.000702s vs 0.001469s) for counting operations.

• **Update Operations:**
  - Customer Data: Customer-centric design is 31% faster (0.000433s vs 0.000628s) as it updates a single document.
  - By Country: Customer-centric design is 21% faster (0.004028s vs 0.005107s) for bulk updates.

• **Delete Operations:**
  - Customer Data: Customer-centric design is 17% faster (0.000337s vs 0.000406s) as it removes all customer data in one operation.
  - By Country: Customer-centric design is 15% faster (0.000934s vs 0.001101s) for bulk deletions.

### Conclusion:
• Choose the **transaction-centric design** if your application frequently performs invoice lookups, transaction counting, or country-based sales analysis.
• Choose the **customer-centric design** if your application focuses on customer profiles, bulk operations, or needs to frequently access complete customer purchase histories.

### Performance Results (Average Time in Seconds)

| Operation | Transaction-Centric | Customer-Centric |
|-----------|-------------------|------------------|
| CREATE - Bulk Insert | 0.011436 | 0.005815 |
| CREATE - Single Insert | 0.000514 | 0.000628 |
| READ - Customer Data Lookup | 0.000688 | 0.000440 |
| READ - Sales by Country | 0.000398 | 0.000771 |
| READ - Invoice Lookup | 0.000405 | 0.000556 |
| READ - Transaction Count | 0.000702 | 0.001469 |
| UPDATE - Customer Data | 0.000628 | 0.000433 |
| UPDATE - By Country | 0.005107 | 0.004028 |
| DELETE - Customer Data | 0.000406 | 0.000337 |
| DELETE - By Country | 0.001101 | 0.000934 |
