# Creating & Processing Data Pipeline

Run StreamSets Data Collector in an Ubuntu VM on Windows 10 (no dual boot) and build a pipeline that masks credit card numbers, converts field types, and adds calculated fields to the NYC taxi sample data. [Video walkthrough](https://www.youtube.com/watch?v=kqVJjWjjOyc)

StreamSets Data Collector is a lightweight engine for routing and processing data streams in real time. I first tried Windows Subsystem for Linux (WSL) through VS Code. It worked but took longer to set up, so this guide uses a VM instead.

## What you'll use

- [StreamSets Data Collector 3.22.3](https://accounts.streamsets.com/install/select/data-collector)
- [VMware Workstation](https://www.vmware.com/products/workstation-pro.html)
- [Ubuntu 22.04.1 LTS](https://apps.microsoft.com/store/detail/ubuntu-22041-lts/9PN20MSR04DW?hl=en-gb&gl=gb)
- OpenJDK 8 (Java 8 JDK, not the JRE)
- Dataset: [NYC Taxi Data](https://docs.streamsets.com/datacollector/sample_data/tutorial/nyc_taxi_data.csv)

StreamSets work falls into five phases: Set Up (environments, deployments, engines, connections), Build (fragments, pipelines, samples), Run (job templates, instances, scheduled tasks, draft runs), Monitor (dashboards, topologies, reports, alerts), and Manage (organization, users, groups, audit, API credentials). This guide covers Set Up, Build, and Run.

## Steps

### Part 1: Set up Data Collector

1. Download the Ubuntu 22.04.1 LTS ISO and install it as a new VM in VMware Workstation.

   Expected result: the Ubuntu installer runs inside the "Ubuntu 64-bit" VM and finishes installing packages.

2. In the VM, open the [Data Collector download page](https://accounts.streamsets.com/install/select/data-collector). Under Target Operating System select Linux Server - For production use, under Download Type select Tarball (Recommended), then select Download.
3. Install Java 8:

   ```bash
   sudo apt-get update && sudo apt-get install openjdk-8-jdk
   ```

4. Download the tarball (release 3.22.3):

   ```bash
   wget https://archives.streamsets.com/datacollector/3.22.3/tarball/activation/streamsets-datacollector-common-3.22.3.tgz
   ```

5. Extract it:

   ```bash
   tar xvzf streamsets-datacollector-common-3.22.3.tgz
   ```

6. Check the open file limit. The default is 1024, and Data Collector needs at least 32768:

   ```bash
   ulimit -n
   ulimit -n 32768
   ulimit -n
   ```

   Expected result: the last command prints `32768`.

7. Start Data Collector from the install folder:

   ```bash
   cd streamsets-datacollector-3.22.3
   bin/streamsets dc
   ```

8. Open the URL the terminal prints, for example `http://<hostname>:18630`. Log in to your StreamSets account if asked and link the Data Collector to it.

### Part 2: Lay out the pipeline

9. Create a new pipeline and place these stages:
   - Directory 1 (origin) > Stream Selector
   - Stream Selector output 1 > Jython Evaluator > Field Masker > Local FS (destination)
   - Stream Selector output 2 > Expression Evaluator 1 > Field Type Converter > Expression Evaluator 2 > Trash
   - Field Masker also connects to the Field Type Converter

   I first used Hadoop FS as the destination. It showed a validation error in the VM, so I switched to Local FS.

### Part 3: Configure the stages

10. Select Directory 1 and open Configuration > Files. Set:
    - Files Directory: `/<base directory>/tutorial/<input folder>` (the folder holding the CSV)
    - File Name Pattern: `nyc_taxi_data.csv`
    - With advanced options shown: Number of Threads `1`, File Name Pattern Mode Glob, Read Order Lexicographically Ascending File Names, Batch Size `1000`, Batch Wait Time `60`
11. On the Directory 1 Data Format tab, set Data Format to Delimited, Delimiter Format Type to Default CSV (ignores empty lines), Lines to Skip to `0`, Compression Format to None, and CSV Parser to Apache Commons. Set Header Line to With Header Line so fields like `/payment_type` exist by name.
12. Select the Stream Selector and, on the Conditions tab, add this condition and route it to output 1 (the Jython Evaluator). Everything else goes to output 2 (Expression Evaluator 1):

    ```
    ${record:value('/payment_type') == 'CRD'}
    ```

13. Open Package Manager, install Jython, then go back to the pipeline.
14. In the Jython Evaluator configuration, enter this script:

    ```python
    try:
      for record in records:
        # Extract the credit card number from the current record
        cc = record.value['credit_card']

        # Check if the credit card number is empty
        if cc == '':
          # Write an error message if the credit card number is empty and continue to the next record
          error.write(record, "Payment type was CRD, but credit card was null")
          continue

        # Mask the credit card number by replacing all but the last four digits with asterisks
        masked_cc = '*' * (len(cc) - 4) + cc[-4:]

        # Initialize the credit card type as an empty string
        cc_type = ''

        # Determine the credit card type based on the starting digits of the credit card number
        if cc.startswith('4'):
          cc_type = 'Visa'
        elif cc.startswith(('51','52','53','54','55')):
          cc_type = 'MasterCard'
        elif cc.startswith(('34','37')):
          cc_type = 'AMEX'
        elif cc.startswith(('300','301','302','303','304','305','36','38')):
          cc_type = 'Diners Club'
        elif cc.startswith(('6011','65')):
          cc_type = 'Discover'
        elif cc.startswith(('2131','1800','35')):
          cc_type = 'JCB'
        else:
          cc_type = 'Other'

        # Update the record with the determined credit card type
        record.value['credit_card_type'] = cc_type

        # Update the record with the masked credit card number
        record.value['credit_card'] = masked_cc

        # Write the updated record to the output
        output.write(record)

    except Exception as e:
      # Write the record and the exception message to the error output if an exception occurs
      error.write(record, e.message)
    ```

15. In Expression Evaluator 1, on the Expressions tab, add Field Output `/credit_card_type` with expression `n/a`.
16. In Local FS, on the Output Files tab, set:
    - Files Prefix: `out_` (instead of the default "SDC" plus Data Collector ID)
    - Directory Template: replace the default datetime template with `/<base directory>/tutorial/destination`
    - Max File Size (MB): `5` or `1`
17. On the Local FS Data Format tab, set Data Format to Delimited and Header Line to With Header Line. Keep the defaults for everything else.
18. In the Field Masker, on the Mask tab, mask all but the last four digits:
    - Fields to Mask: `/credit_card`
    - Mask Type: Regular Expression
    - Regular Expression: `(.*)([0-9]{4})`
    - Groups to Show: `2`
19. In the Field Type Converter, on the Conversions tab, convert `/dropoff_datetime` and `/pickup_datetime` to DATETIME with Date Format `yyyy-MM-dd HH:mm:ss`.
20. Select the plus to add a second conversion, and convert these fields to DOUBLE:

    ```
    /fare_amount
    /dropoff_latitude
    /dropoff_longitude
    /mta_tax
    /pickup_latitude
    /pickup_longitude
    /surcharge
    /tip_amount
    /tolls_amount
    /total_amount
    ```

21. In Expression Evaluator 2, on the Expressions tab, add three field expressions:

    | Output field | Expression |
    |---|---|
    | `/pickup_location` | `${record:value('/pickup_latitude')}, ${record:value('/pickup_longitude')}` |
    | `/dropoff_location` | `${record:value('/dropoff_latitude')}, ${record:value('/dropoff_longitude')}` |
    | `/trip_revenue` | `${record:value('/total_amount') - record:value('/tip_amount')}` |

    The `/trip_revenue` expression subtracts the tip from the total fare.

### Part 4: Run the pipeline

22. Start the pipeline. If you are rerunning an earlier pipeline or one you stopped, use Reset Origin & Start so it reads the file again.

    Expected result: the pipeline shows RUNNING. The Summary tab's Record Count shows about 5,386 input, 5,191 output, and 2,628 error records, and the Record Throughput chart shows input, output, and error rates. My run took about 15 minutes.

## What I learned

- Check every directory path and stage setting. A small miss can make the whole pipeline fail, or run with no output and no errors.
- Records can be split by condition, transformed with Jython or expressions, and masked before they are written.
- A running pipeline with steady throughput is the goal: data moves from source to destination and is transformed along the way.
